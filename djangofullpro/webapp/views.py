# from django.middleware.csrf import get_token
# from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view,action,permission_classes
from rest_framework.response import Response
from rest_framework import status,viewsets
from .serializers import SignupSerializer, MyTokenObtainPairSerializer,QuestionSerializer,DashboardSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Question, Choice,Vote
from django.db.models import Sum,F
from django.db import transaction,IntegrityError
from django.db.models.functions import Coalesce
from .pagination import DashboardPagination
from django.shortcuts import get_object_or_404
from .permissions import IsOwnerPermission
from rest_framework.throttling import UserRateThrottle

class VoteThrottle(UserRateThrottle):
    rate="20/min"
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
        
@api_view(['POST'])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User created successfully"},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"status_code": 200,"message": "Logout successful"},status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status_code": 400,"error": str(e)},status=status.HTTP_400_BAD_REQUEST)

class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsOwnerPermission]
    serializer_class = QuestionSerializer
    pagination_class = DashboardPagination
    
    def get_queryset(self):
        return Question.objects.all().order_by('-created_at','-id')
    
    def get_permissions(self):

        if self.action in ['update','partial_update','destroy']:
            return [
                IsAuthenticated(),
                IsOwnerPermission()
            ]

        return [
            IsAuthenticated()
        ] 
          
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['post'], throttle_classes=[VoteThrottle])
    
    def vote(self, request, pk=None):
        option_number = request.data.get('option_number')
        if not option_number:
            return Response({"error": "option_number is required"},status=status.HTTP_400_BAD_REQUEST)
        question = self.get_object()
        choice = get_object_or_404(Choice,question=question,option_number=option_number)
        # check already voted
        try:
            with transaction.atomic():
                # save vote
                Vote.objects.create(user=request.user,question=question,choice=choice)
                choice.votes  = F('votes') + 1
                choice.save()
                choice.refresh_from_db()
        except IntegrityError:
            return Response({"error": "You already voted for this poll"},status=400)
        return Response({"message": "Vote submitted","choice": choice.choice_text,"votes": choice.votes},status=status.HTTP_200_OK)
            
class DashboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DashboardSerializer
    pagination_class = DashboardPagination

    def get_queryset(self):
        return Question.objects.select_related("user").prefetch_related('choices').annotate(total_votes=Coalesce(Sum('choices__votes'),0)).order_by('-created_at','-id')                       
        
# @require_http_methods(["GET"])
# def csrf_token_view(request):
#     """
#     Call this endpoint first to get a CSRF token.
#     """
#     return JsonResponse({
#         "csrfToken": get_token(request)
#     })