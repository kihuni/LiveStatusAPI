from django.contrib.auth.tokens import PasswordResetTokenGenerator

class ResetPasswordTokenGenerator(PasswordResetTokenGenerator):
    pass

reset_password_token = ResetPasswordTokenGenerator()
