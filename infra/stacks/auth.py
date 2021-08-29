
from aws_cdk import core as cdk
from aws_cdk import aws_cognito as cognito
from aws_cdk.aws_cognito import UserVerificationConfig, VerificationEmailStyle, UserInvitationConfig, SignInAliases

from config import ResolvedSettings


class AuthStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, *,
        settings: ResolvedSettings, client_id,
        client_secret, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.pool = cognito.UserPool(
            self, f"{settings.prefix}-user-pool",
            user_pool_name=f"{settings.prefix}-user-pool",
            self_sign_up_enabled=True,
            #user_verification=UserVerificationConfig(
            #    email_subject='Please verify you signed up cfchou.me',
            #    email_style=VerificationEmailStyle.CODE,
            #    email_body=f"Thanks for signing up {settings.app_name}! Your "
            #               f"verification code is {{####}}",
            #    sms_message=f"Thanks for signing up {settings.app_name}! Your "
            #                f"verification code is {{####}}"
            #),
            #sign_in_aliases=SignInAliases(email=True, username=True),
            #user_invitation=UserInvitationConfig(
            #    email_subject="Invite to join our awesome app!",
            #    email_body="Hello {username}, you have been invited to join our awesome app! Your temporary password is {####}",
            #    sms_message="Your temporary password for our awesome app is {####}"
            #)
        )

        self.provider = cognito.UserPoolIdentityProviderGoogle(
            self, f"{settings.prefix}-google",
            client_id=settings.secrets.client_id,
            client_secret=settings.secrets.client_secret,
            scopes=["profile", "email", "openid"]
        )

