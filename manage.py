#!/usr/bin/env python
import os
import sys

from decouple import config


if __name__ == "__main__":

    env = config('ENVIRONMENT')
    settings = 'sendhut.settings.{}'.format(env)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
