from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.books.urls', namespace='books')),
    path('readers/', include('apps.readers.urls', namespace='readers')),
    path('loans/', include('apps.loans.urls', namespace='loans')),
    path('ai/', include('apps.ai_assistant.urls', namespace='ai_assistant')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
