from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from . import views, api, download, bulkDownload
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import routers
from django.views.generic import RedirectView

router = routers.DefaultRouter()


urlpatterns = patterns('',
    				   url(r'^api/list_labels$', api.ListLables.as_view(), name='api-list-labels'),
					   url(r'^api/list_mails/$', api.ListMails.as_view(), name='api-list-mails'),
					   url(r'^api/get_user$', api.getUser.as_view(), name='api-get-user'),
					   #url(r'^api/initiate_download$', api.InitiateDownload.as_view(), name='api-initiate-download'),
					   
					   url(r'^bulkdownload/mydownloads/', bulkDownload.ListDownloadRequest.as_view(), name='bulkDownload-request-list'),
					   url(r'^initiate_download/$', bulkDownload.DownloadRequest.as_view(), name='bulkDownload-download'),
					   url(r'^remove_data/$', bulkDownload.RemoveData.as_view(), name='remove_data'),

					   url(r'^download/download_mails/$', download.ListMails.as_view(), name='download-mails'),
					   url(r'^api/v.0.1/', include(router.urls)),
					   url(r'^signup/', views.signup, name='signup'),
					   url(r'oauth2callback', views.oauth2callback, name='return'),
					   url(r'^logout/', views.loggingout, name='logging'),
					   url(r'^login/', views.user_login, name='user-login'),
					   url(r'^email-extractor/', views.email_extractor, name='email-extractor'),
					   url(r'^$', views.home, name='home'),
					  )

