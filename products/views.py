import json

from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Q, Avg
from django.core.exceptions import FieldError

from products.models import Category, Product

class CategoryView(View):
    def get(self,request):
        category_lists = [
            {
            'category_id' : category.id,
            'name'        : category.name,
            'image_url'   : category.image_url
            }
        for category in Category.objects.all()]        
        return JsonResponse({'MESSAGE':'SUCCESS','category_lists':category_lists}, status=200)

class ProductListView(View):
    def get(self,request):
        try: 
            ordering    = request.GET.get('ordering','-price')
            category_id = request.GET.get('category-id', None)

            q=Q()
            if category_id:
                q = Q(category_id=category_id)
            products = Product.objects.filter(q).annotate(star_rating=Avg('review__star_rating')).order_by(ordering)
            
            if len(products)==0:
                return JsonResponse({'MESSAGE':'INVALID_CATEGORY_ID'}, status=401)
            
            product_lists = [
                {
                    'id'              : product.id,
                    'name'            : product.name,
                    'price'           : product.price,
                    'manufacturer'    : product.manufacturer,
                    'discount_rate'   : product.discount_rate,
                    'star_rating'     : round(product.review_set.all().aggregate(Avg('star_rating'))['star_rating__avg'],1),
                    'review_number'   : product.review_set.count(),
                    'is_freedelivery' : product.is_freedelivery,
                    'thumbnail_image' : product.thumbnail_image
                } for product in products]
            
            return JsonResponse({'MESSAGE':'SUCCESS','product_lists':product_lists}, status=200)
        
        except FieldError:
            return JsonResponse({'MESSAGE':'INVALID_ORDERING_METHOD'}, status=401)