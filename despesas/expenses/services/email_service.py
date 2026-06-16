import resend
from decouple import config

resend.api_key = config("RESEND_API_KEY")


def send_password_reset_email(to_email, token):
    reset_link = f"{config('FRONTEND_URL')}/reset-password?token={token}"

    resend.Emails.send(
        {
            "from": "Control Despesas <onboarding@resend.dev>",
            "to": to_email,
            "subject": "Recuperar password",
            "html": f"""
            <h2>Recuperação de password</h2>
            <p>Clica no link abaixo:</p>
            <a href="{reset_link}">Reset password</a>
            <p>Este link expira em breve.</p>
        """,
        }
    )
