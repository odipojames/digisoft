from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserSerializer, LoginSerializer, TokenPairSerializer,ChangePasswordSerializer,ChequeSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import CustomUser, Cheque
from django.core.exceptions import ValidationError
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import authentication_classes, permission_classes






@authentication_classes([])#bypass auth and permisions
@permission_classes([])
class UserRegistration(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@authentication_classes([])
@permission_classes([])
class Login(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

@authentication_classes([])
@permission_classes([])
class TokenRefresh(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        refresh = request.data.get('refresh')
        serializer = TokenPairSerializer(data={'refresh': refresh})
        serializer.is_valid(raise_exception=True)
        token = RefreshToken(refresh)
        return Response({'access': str(token.access_token)})
    
    
class Deposit(APIView):
    permission_classes = [IsAuthenticated]

    def validate_amount(self, amount):
        if amount is None:
            raise ValidationError('Amount is required.')
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValidationError('Amount must be greater than zero.')
        except ValueError:
            raise ValidationError('Amount must be a valid number.')

    def post(self, request):
        amount = request.data.get('amount')
        try:
            self.validate_amount(amount)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        # Assuming 'balance' is a field in your User model
        user.balance += Decimal(amount)
        user.save()  # Save the updated balance to the database
        return Response({'message': 'Deposit successful'}, status=status.HTTP_200_OK)

class CheckBalance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'account_number': user.account_number, 'name': user.first_name + ' ' + user.last_name,
                         'balance': user.balance}, status=status.HTTP_200_OK)

class StopCheque(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cheque_number = request.data.get('cheque_number')
        
        # Check if cheque_number is provided
        if cheque_number is None:
            raise ValidationError({'cheque_number': 'Cheque number is required.'})

        user = request.user
        try:
            cheque = Cheque.objects.get(cheque_number=cheque_number)
            print(cheque)
            cheque.status = 'Stopped'
            cheque.save()
            return Response({'message': 'Cheque stopped successfully'}, status=status.HTTP_200_OK)
        except Cheque.DoesNotExist:
            return Response({'error': 'Cheque not found or does not belong to the user'},
                            status=status.HTTP_404_NOT_FOUND)
            
            
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        # Check if old password is correct
        if not user.check_password(serializer.validated_data['old_pin']):
            return Response({'error': 'Old pin is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        # Change password
        user.set_password(serializer.validated_data['new_pin1'])
        user.save()

        return Response({'message': 'Pin changed successfully'}, status=status.HTTP_200_OK)    


class CreateCheque(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChequeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)