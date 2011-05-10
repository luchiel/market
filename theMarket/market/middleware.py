from market.models import User, Basket

class UserMiddleware:
    def process_request(self, request):
        request.user = None
        request.basket = None
        if 'user_id' in request.session:
            try:
                request.user = User.objects.get(id=request.session['user_id'])
                if not Basket.objects.filter(user=request.user):
                    request.basket = Basket(user=request.user)
                    request.basket.save()
                else:
                    request.basket = Basket.objects.get(user=request.user)
            except User.DoesNotExist:
                pass
        else:
            if not Basket.objects.filter(session_id=request.session.session_key):
                request.basket = Basket(session_id=request.session.session_key)
                request.basket.save()
            else:
                request.basket = Basket.objects.get(session_id=request.session.session_key)
