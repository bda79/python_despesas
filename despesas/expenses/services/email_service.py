from django.core.mail import EmailMultiAlternatives


def send_password_reset_email(to_email, reset_link):

    text_content = f"""
    Recuperação de password

    Utilize o seguinte link:
    {reset_link}
    """

    html_content = f"""
    <h2>Recuperação de password</h2>
    <p>Clique no link abaixo:</p>
    <p>
        <a href="{reset_link}">Reset password</a>
    </p>
    <p>Este link expira em breve.</p>
    """

    msg = EmailMultiAlternatives(
        subject="Recuperar password",
        body=text_content,
        to=[to_email],
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()
