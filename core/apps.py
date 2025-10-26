from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        import core.signals  # noqa

        # Ensure the django.contrib.sites Site object reflects the configured
        # SITE_DOMAIN / SITE_NAME so emails rendered by allauth (and other
        # libraries) don't show the default "example.com" site.
        try:
            from django.conf import settings

            # Importing models can fail during migrations or when the DB is not
            # yet available; guard against that.
            from django.contrib.sites.models import Site
            from django.db.utils import OperationalError, ProgrammingError

            domain = getattr(settings, "SITE_DOMAIN", None)
            name = getattr(settings, "SITE_NAME", None)

            if domain or name:
                try:
                    site = Site.objects.get(pk=settings.SITE_ID)
                    changed = False
                    if domain and site.domain != domain:
                        site.domain = domain
                        changed = True
                    if name and site.name != name:
                        site.name = name
                        changed = True
                    if changed:
                        site.save()
                except Site.DoesNotExist:
                    # Create the site record if it doesn't exist
                    Site.objects.create(
                        id=settings.SITE_ID,
                        domain=domain or "checklist.casa",
                        name=name or "Checklist.casa",
                    )
        except (OperationalError, ProgrammingError):
            # Database isn't ready (migrations running) — skip updating Site.
            pass
        except Exception:
            # Best-effort only; don't let site fixes break startup.
            pass
