#!/usr/bin/env python
import os
import sys
import logging
from opentelemetry.instrumentation.django import DjangoInstrumentor

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dataselectie.settings")


    def response_hook(span, request, response):
        if span and span.is_recording():
            email = request.get_token_subject
            if getattr(request, "get_token_claims", None) and "email" in request.get_token_claims:
                email = request.get_token_claims["email"]
                span.set_attribute("user.AuthenticatedId", email)

    # Instrument Django app
    DjangoInstrumentor().instrument(response_hook=response_hook)
    print("django instrumentor enabled")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
