from django.urls import path
from .views import home, task_list, task_create, task_detail, task_done, task_not_done, task_delete, task_edit_form, task_edit_model_form, add_comment, delete_comment
from .views import TaskListAPI, TaskDetailAPI, TaskClassListAPI
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Task Planner rajapintadokumentaatio",
      default_version='v1',
      description="Tehtäväkorttisovelluksen API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@taskplanner.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', home, name='home'),
    path('tasks/', task_list, name='task_list'),
    path('tasks/add/', task_create, name='task_create'),
    path('tasks/<int:task_id>/delete', task_delete, name='task_delete'),
    path('tasks/<int:task_id>/task_done', task_done, name='task_done'),
    path('tasks/<int:task_id>/task_not_done', task_not_done, name='task_not_done'),
    path('tasks/<int:task_id>/', task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit_form', task_edit_form, name='task_edit_form'),
    path('tasks/<int:task_id>/edit_model_form', task_edit_model_form, name='task_edit_model_form'),
    path('task/<int:task_id>/add_comment/', add_comment, name='add_comment'),
    path('task/<int:task_id>/comment/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    #path("api/tasks/", TaskListAPI.as_view({'get': 'list'}), name="task_list_api"),
    path("api/tasks/", TaskListAPI.as_view(), name="task_list_api"),
    path("api/tasks/<int:pk>/", TaskDetailAPI.as_view(), name="task_detail_api"),
    path("api/task_classes/", TaskClassListAPI.as_view(), name="task_classes"),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]


