from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.models import UserProfile

from .models import ExerciseSession, ExerciseTemplate, RehabPlan,  ExerciseResult
from .serializers import (
	ExerciseSessionSerializer,
	ExerciseTemplateSerializer,
	RehabPlanCreateSerializer,
	RehabPlanDetailSerializer,
	SessionCompleteSerializer,
	SessionStartSerializer,
	DoctorFeedbackSerializer,
)
from .models import DoctorFeedback


class ExerciseTemplateListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		templates = ExerciseTemplate.objects.all().order_by("name")
		serializer = ExerciseTemplateSerializer(templates, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class RehabPlanCreateView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		profile = getattr(request.user, "profile", None)
		role = getattr(profile, "role", None)
		if role != UserProfile.ROLE_DOCTOR:
			return Response(
				{"detail": "Only doctor users can create rehab plans."},
				status=status.HTTP_403_FORBIDDEN,
			)

		serializer = RehabPlanCreateSerializer(data=request.data, context={"request": request})
		serializer.is_valid(raise_exception=True)
		plan = serializer.save()

		response_serializer = RehabPlanDetailSerializer(plan)
		return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class RehabPlanDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, plan_id):
		plan = get_object_or_404(
			RehabPlan.objects.select_related("doctor", "patient").prefetch_related("plan_exercises__exercise"),
			id=plan_id,
		)

		profile = getattr(request.user, "profile", None)
		role = getattr(profile, "role", None)

		if role == UserProfile.ROLE_DOCTOR and plan.doctor_id != request.user.id:
			return Response({"detail": "You can only view plans you created."}, status=status.HTTP_403_FORBIDDEN)

		if role == UserProfile.ROLE_PATIENT and plan.patient_id != request.user.id:
			return Response({"detail": "You can only view plans assigned to you."}, status=status.HTTP_403_FORBIDDEN)

		if role not in {UserProfile.ROLE_DOCTOR, UserProfile.ROLE_PATIENT}:
			return Response({"detail": "Access denied for this user role."}, status=status.HTTP_403_FORBIDDEN)

		serializer = RehabPlanDetailSerializer(plan)
		return Response(serializer.data, status=status.HTTP_200_OK)


class SessionStartView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		profile = getattr(request.user, "profile", None)
		role = getattr(profile, "role", None)
		if role != UserProfile.ROLE_PATIENT:
			return Response(
				{"detail": "Only patient users can start rehab sessions."},
				status=status.HTTP_403_FORBIDDEN,
			)

		serializer = SessionStartSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		plan = get_object_or_404(RehabPlan, id=serializer.validated_data["plan_id"])
		if plan.patient_id != request.user.id:
			return Response(
				{"detail": "You can only start sessions for plans assigned to you."},
				status=status.HTTP_403_FORBIDDEN,
			)

		session = ExerciseSession.objects.create(patient=request.user, plan=plan)
		response_serializer = ExerciseSessionSerializer(session)
		return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SessionCompleteView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, session_id):
		profile = getattr(request.user, "profile", None)
		role = getattr(profile, "role", None)
		if role != UserProfile.ROLE_PATIENT:
			return Response(
				{"detail": "Only patient users can complete rehab sessions."},
				status=status.HTTP_403_FORBIDDEN,
			)

		session = get_object_or_404(ExerciseSession, id=session_id)

		if session.patient_id != request.user.id:
			return Response(
				{"detail": "You can only complete your own sessions."},
				status=status.HTTP_403_FORBIDDEN,
			)

		if session.completed_at is not None:
			return Response(
				{"detail": "Session is already completed."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		exercise_results = request.data.get("exercise_results", [])
		body_part_scores = request.data.get("body_part_scores", [])

		if not isinstance(exercise_results, list) or not isinstance(body_part_scores, list):
			return Response(
				{"detail": "Both exercise_results and body_part_scores must be lists."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		results_to_create = []
		for idx, item in enumerate(exercise_results):
			name = item.get("name")
			reps = item.get("reps", 0)
			accuracy = item.get("accuracy", 0.0)
			duration = item.get("duration", 0.0)
			
			if not name:
				continue
				
			exercise = ExerciseTemplate.objects.filter(name=name).first()
			if not exercise:
				continue
				
			results_to_create.append(
				ExerciseResult(
					session=session,
					exercise=exercise,
					reps=reps,
					accuracy=accuracy,
					duration=duration,
					order=idx + 1
				)
			)

		ExerciseResult.objects.bulk_create(results_to_create)

		from django.utils import timezone
		session.body_part_scores = body_part_scores
		session.completed_at = timezone.now()
		session.save(update_fields=["body_part_scores", "completed_at"])

		return Response({
			"message": "Session completed successfully",
			"exercise_count": len(results_to_create)
		}, status=status.HTTP_200_OK)


class PatientSessionHistoryView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, patient_id):
		profile = getattr(request.user, "profile", None)
		if not profile or profile.role != UserProfile.ROLE_DOCTOR:
			return Response({"detail": "Only doctors can view patient history."}, status=status.HTTP_403_FORBIDDEN)

		sessions = ExerciseSession.objects.filter(patient_id=patient_id).order_by("-started_at")
		serializer = ExerciseSessionSerializer(sessions, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class PatientStreakView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, patient_id):
		profile = getattr(request.user, "profile", None)
		if not profile or profile.role != UserProfile.ROLE_DOCTOR:
			return Response({"detail": "Only doctors can view patient streak data."}, status=status.HTTP_403_FORBIDDEN)

		dates = ExerciseSession.objects.filter(
			patient_id=patient_id, 
			completed_at__isnull=False
		).values_list('completed_at__date', flat=True).distinct().order_by("-completed_at__date")

		return Response({
			"patient_id": patient_id,
			"active_days": list(dates),
			"total_days": len(dates)
		}, status=status.HTTP_200_OK)


class PatientPlanListView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		profile = getattr(request.user, "profile", None)
		if not profile or profile.role != UserProfile.ROLE_PATIENT:
			return Response({"detail": "Only patients can view their assigned plans."}, status=status.HTTP_403_FORBIDDEN)

		plans = RehabPlan.objects.filter(patient=request.user).prefetch_related("plan_exercises__exercise")
		serializer = RehabPlanDetailSerializer(plans, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class MySessionHistoryView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		profile = getattr(request.user, "profile", None)
		if not profile or profile.role != UserProfile.ROLE_PATIENT:
			return Response({"detail": "Only patients can view their history."}, status=status.HTTP_403_FORBIDDEN)

		sessions = ExerciseSession.objects.filter(patient=request.user).order_by("-started_at")
		serializer = ExerciseSessionSerializer(sessions, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class SessionDetailView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, session_id):
		session = get_object_or_404(ExerciseSession, id=session_id)
		
		# Check ownership
		profile = getattr(request.user, "profile", None)
		if session.patient_id != request.user.id and (not profile or profile.role != UserProfile.ROLE_DOCTOR):
			return Response({"detail": "You do not have permission to view this session."}, status=status.HTTP_403_FORBIDDEN)

		serializer = ExerciseSessionSerializer(session)
		return Response(serializer.data, status=status.HTTP_200_OK)

class DoctorFeedbackCreateView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request):
		profile = getattr(request.user, "profile", None)
		if not profile or profile.role != UserProfile.ROLE_DOCTOR:
			return Response({"detail": "Only doctors can submit feedback."}, status=status.HTTP_403_FORBIDDEN)

		serializer = DoctorFeedbackSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		session = serializer.validated_data["session"]
		patient = serializer.validated_data["patient"]
		
		if session.patient != patient:
			return Response({"detail": "Session does not belong to the specified patient."}, status=status.HTTP_400_BAD_REQUEST)
			
		if DoctorFeedback.objects.filter(session=session).exists():
			return Response({"detail": "Feedback already submitted for this session."}, status=status.HTTP_400_BAD_REQUEST)

		feedback = serializer.save(doctor=request.user)
		return Response(DoctorFeedbackSerializer(feedback).data, status=status.HTTP_201_CREATED)

