from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("home.urls")),
    path(
        "services/",
        include(("services.urls", "services"), namespace="services"),
    ),
    path("bag/", include("bag.urls", namespace="bag")),
    path("checkout/", include("checkout.urls", namespace="checkout")),
    path("accounts/", include("accounts.urls")),
    path("admin-panel/", include("adminpanel.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "project_4.views.error_403"
handler404 = "project_4.views.error_404"
handler500 = "project_4.views.error_500"
