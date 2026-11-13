from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .medicine_info import MedicineLookupError, lookup_medicine_information
from .models import DiseaseInformation, Symptom, SymptomAssessment
from .serializers import (
    AssessmentCreateSerializer,
    DiseaseInformationSerializer,
    SymptomAssessmentSerializer,
    SymptomSerializer,
)
from .services import analyze_symptoms


class SymptomListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        symptoms = Symptom.objects.filter(is_active=True)
        category = request.query_params.get('category', '').strip()
        if category:
            symptoms = symptoms.filter(category__iexact=category)
        return Response(SymptomSerializer(symptoms, many=True).data)


class AssessmentListCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assessments = (
            SymptomAssessment.objects.filter(user=request.user)
            .prefetch_related('symptoms')
        )
        return Response(SymptomAssessmentSerializer(assessments, many=True).data)

    def post(self, request):
        serializer = AssessmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptoms = list(Symptom.objects.filter(
            pk__in=serializer.validated_data['symptom_ids'],
            is_active=True,
        ))
        assessment = SymptomAssessment.objects.create(
            user=request.user,
            duration=serializer.validated_data['duration'],
            additional_notes=serializer.validated_data.get('additional_notes', ''),
            assessment_summary=analyze_symptoms(symptoms),
        )
        assessment.symptoms.set(symptoms)
        return Response(
            SymptomAssessmentSerializer(assessment).data,
            status=status.HTTP_201_CREATED,
        )


class AssessmentDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        assessment = get_object_or_404(
            SymptomAssessment.objects.prefetch_related('symptoms'),
            pk=pk,
            user=request.user,
        )
        return Response(SymptomAssessmentSerializer(assessment).data)


class DiseaseInformationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is not None:
            disease = get_object_or_404(
                DiseaseInformation.objects.prefetch_related('symptoms'),
                pk=pk,
                is_active=True,
            )
            return Response(DiseaseInformationSerializer(disease).data)
        diseases = DiseaseInformation.objects.filter(is_active=True).prefetch_related('symptoms')
        return Response(DiseaseInformationSerializer(diseases, many=True).data)


class MedicineInformationAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'detail': 'Provide a medicine name in the q parameter.'}, status=400)
        try:
            medicines = lookup_medicine_information(query)
        except ValueError as error:
            return Response({'detail': str(error)}, status=400)
        except MedicineLookupError as error:
            return Response({'detail': str(error)}, status=502)
        return Response({
            'results': medicines,
            'source': 'U.S. FDA openFDA drug product labeling',
            'disclaimer': (
                'Educational information only. Do not rely on these labels for medical '
                'care decisions; consult a healthcare professional.'
            ),
        })
