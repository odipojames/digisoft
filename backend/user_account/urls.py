from django.urls import path
from .views import UserRegistration, Login, TokenRefresh,Deposit, CheckBalance, StopCheque, ChangePassword,CreateCheque

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('token/refresh/', TokenRefresh.as_view(), name='token_refresh'),
    path('deposit/', Deposit.as_view(), name='deposit'),
    path('check_balance/', CheckBalance.as_view(), name='check_balance'),
    path('stop_cheque/', StopCheque.as_view(), name='stop_cheque'),
    path('change_pin/', ChangePassword.as_view(), name='change_password'),
    path('create_cheque/', CreateCheque.as_view(), name='create_cheque'),
]

