from djoser import email


class ActivationEmail(email.ActivationEmail):
    template_name = 'emails/djoser/activation.html'


class ConfirmationEmail(email.ConfirmationEmail):
    template_name = 'emails/djoser/confirmation.html'
    

class PasswordResetEmail(email.PasswordResetEmail):
    template_name = 'emails/djoser/password_reset.html'
    

class PasswordChangedConfirmationEmail(email.PasswordChangedConfirmationEmail):
    template_name = 'emails/djoser/password_changed_confirmation.html'
    