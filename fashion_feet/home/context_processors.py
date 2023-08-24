from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

def category_context(request):
    category = Category.objects.all()  # Get the category you want to pass to the template
    return {'category': category}

