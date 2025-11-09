from django.urls import path

from .views import (
    ForgotPasswordView,
    LoginView,
    PaymentDetailView,
    PremiumSubscriptionView,
    ReceiptUploadView,
    ResetPasswordView,
    StudentAPIView,
    StudentDetailAPIView,
    TrialActivationView,
    UserDetailAPIView,
    UserRegisterAPIView,
    UserSubscriptionView,
    ResendOTPView
)

urlpatterns = [
    path("userregister/", UserRegisterAPIView.as_view(), name="user-register"), 
    path("userregister/<uuid:pk>/", UserDetailAPIView.as_view(), name="user-detail"), 
    path("login/", LoginView.as_view(), name="login"),  
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"), 
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"), 
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("subscriptions/trial/activate/", TrialActivationView.as_view(), name="trial-activation"),
    path("subscriptions/premium/create/", PremiumSubscriptionView.as_view(), name="premium-subscription"),
    path("subscriptions/payment-details/", PaymentDetailView.as_view(), name="payment-details"),
    path("subscriptions/<str:subscription_id>/receipt/", ReceiptUploadView.as_view(), name="receipt-upload"),
    path("subscriptions/user/<uuid:user_id>/", UserSubscriptionView.as_view(), name="user-subscription"),
    path("students/", StudentAPIView.as_view(), name="students"),
    path("students/<uuid:student_id>/", StudentAPIView.as_view(), name="student-detail"),
    path("students-by-owner/<uuid:owner_id>/", StudentDetailAPIView.as_view(), name="student-owner-detail"),
]
