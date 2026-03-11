#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studio.settings')

    # Monkeypatch for Python 3.14 + Django compatibility issue
    try:
        import django.template.context
        
        def patched_base_context_copy(self):
            obj = self.__new__(self.__class__)
            obj.__dict__ = self.__dict__.copy()
            if hasattr(self, 'dicts'):
                obj.dicts = self.dicts[:]
            return obj
            
        django.template.context.BaseContext.__copy__ = patched_base_context_copy
    except (ImportError, AttributeError):
        pass

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
