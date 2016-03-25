from .models import public_snapshot


def add_public_snapshot(request):
    return {
        'PUBLIC_SNAPSHOT': public_snapshot()
    }
