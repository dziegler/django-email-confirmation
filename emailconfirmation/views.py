from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.conf import settings
from emailconfirmation.models import EmailConfirmation, EmailAddress

def confirm_email(request, confirmation_key):
    confirmation_key = confirmation_key.lower()
    email_address = EmailConfirmation.objects.confirm_email(confirmation_key)
    return render_to_response("emailconfirmation/confirm_email.html", {
        "email_address": email_address,
    }, context_instance=RequestContext(request))

@require_POST
def send_confirmation(request,
                      template_name="emailconfirmation/attempts_exceeded.html",
                      success_url=None):
    if request.user.is_authenticated():
        if success_url is None:
            success_url = request.REQUEST.get('next',settings.LOGIN_REDIRECT_URL)
        
        if hasattr(settings,'EMAIL_CONFIRMATION_ATTEMPTS'):
            EMAIL_CONFIRMATION_ATTEMPTS = settings.EMAIL_CONFIRMATION_ATTEMPTS
        else:
            EMAIL_CONFIRMATION_ATTEMPTS = None
        
        bad_addresses = []
        for email_address in EmailAddress.objects.filter(user=request.user,verified=False):
            if EMAIL_CONFIRMATION_ATTEMPTS and \
            email_address.emailconfirmation_set.count() > EMAIL_CONFIRMATION_ATTEMPTS:
                bad_addresses.append(email_address)
            else:
                EmailConfirmation.objects.send_confirmation(email_address)
        
        if bad_addresses:
            return render_to_response(template_name,
                                      {"bad_addresses": bad_addresses},
                                      context_instance=RequestContext(request))
        else:
            return HttpResponseRedirect(success_url)
    else:
        return redirect_to_login