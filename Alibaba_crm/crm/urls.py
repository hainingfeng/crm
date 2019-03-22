"""Alibaba_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from crm import views

urlpatterns = [
    # 展示客户
    # 公户展示
    # url(r'^customer_list/',views.customer_list,name='customer_list'),
    url(r'^customer_list/',views.CustomerList.as_view(),name='customer_list'),
    # 私户展示
    # url(r'^my_customer/',views.customer_list,name='my_customer'),
    url(r'^my_customer/',views.CustomerList.as_view(),name='my_customer'),

    url(r'^user_list/',views.user_list),
    url(r'^user_lists/',views.users_lists),

    # 添加客户
    # url(r'^customer_add/',views.customer_add,name='customer_add'),
    url(r'^customer_add/',views.customer_change,name='customer_add'),
    # 编辑客户
    # url(r'^customer_edit/(\d+)',views.customer_edit,name='customer_edit'),
    url(r'^customer_edit/(\d+)',views.customer_change,name='customer_edit'),

    # 展示记录跟进表
    url(r'^consult_list/(?P<customer_id>\d+)',views.consult_list,name='consult_list'),
    # 添加记录跟进表
    url(r'^consult_add/',views.consult_add,name='consult_add'),

    # 编辑记录跟进表
    url(r'^consult_edit/(\d+)', views.consult_edit, name='consult_edit'),

    # 展示报名记录
    url(r'^enrollment_list/(?P<customer_id>\d+)', views.enrollment_list, name='enrollment_list'),

    # 添加报名记录
    url(r'^enrollment_add/(?P<customer_id>\d+)', views.enrollment_add, name='enrollment_add'),

    # 编辑报名记录
    url(r'^enrollment_edit/(?P<record_id>\d+)', views.enrollment_edit, name='enrollment_edit'),

    # 展示班级
    url(r'^class_list/',views.ClassList.as_view(),name='class_list'),

    # 添加班级
    url(r'^class_add/', views.classes, name='class_add'),

    # 编辑班级
    url(r'^class_edit/(\d+)', views.classes, name='class_edit'),

    # 展示课程记录
    url(r'^course_record_list/(?P<class_id>\d+)', views.CourseRecordList.as_view(), name='course_record_list'),


    # 添加课程记录
    url(r'^course_record_add/(?P<class_id>\d+)', views.course_record, name='course_record_add'),

    # 编辑课程记录
    url(r'^course_record_edit/(?P<course_record_id>\d+)', views.course_record, name='course_record_edit'),

    # 展示学习记录
    url(r'^study_record_list/(?P<course_record_id>\d+)', views.study_record, name='study_record_list'),
]
