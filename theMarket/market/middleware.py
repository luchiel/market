from market.models import User

class UserMiddleware:
    def process_request(self, request):
        request.user = None
        if 'user_id' in request.session:
            try:
                request.user = User.objects.get(id=request.session['user_id'])
            except User.DoesNotExist:
                pass
