from django.contrib import admin
from gextracto.models import FlowModel, CredentialsModel, UserData, BulkRequestId, TaskId




admin.site.register(FlowModel)
admin.site.register(CredentialsModel)
admin.site.register(UserData)
admin.site.register(BulkRequestId)
admin.site.register(TaskId)
