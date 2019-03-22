from django.shortcuts import render, redirect, HttpResponse, reverse
from crm import models
from crm.forms import RegForm, CustomerForm, ConsultForm, EnrollmentForm,ClassListForm,CourseRecordForm,StudyRecordForm
import hashlib
from crm.utils.pagination import Pagination
from crm.utils.url import reverse_url,rev_url
from django.views import View
from django.db.models import Q
from django.conf import settings
from django.db import transaction
from django.forms import modelformset_factory


def index(request):
    return HttpResponse('index')


def login(request):
    err_msg = ''
    if request.method == 'POST':
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        print(user, pwd)
        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        pwd = md5.hexdigest()
        obj = models.UserProfile.objects.filter(username=user, password=pwd, is_active=True).first()
        print(obj)
        if obj:
            request.session['user_id'] = obj.pk
            # return redirect('/index/')
            return redirect(reverse('customer_list'))
        err_msg = '用户名或密码错误'
    return render(request, 'login.html', locals())


def logout(request):
    request.session.flush()
    return redirect(reverse('login'))


def reg(request):
    form_obj = RegForm()
    print('form_obj', form_obj)
    if request.method == 'POST':
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/login/')
    return render(request, 'reg.html', locals())


def customer_list(request):
    if request.path == reverse('customer_list'):
        all_customer = models.Customer.objects.filter(consultant__isnull=True)
    else:
        all_customer = models.Customer.objects.filter(consultant=request.account)
    return render(request, 'customer_list.html', locals())


class CustomerList(View):
    def get(self, request):
        q = self.search(['qq', 'name'])
        if request.path == reverse('customer_list'):
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True)
        else:
            all_customer = models.Customer.objects.filter(q, consultant=request.account)

        pager = Pagination(request.GET.get('page', '1'), all_customer.count(), request.GET.copy(),2)
        # return render(request, 'customer_list.html', locals())
        return render(request, 'customer_list.html', {
            'all_customer': all_customer[pager.start:pager.end],
            'page_html': pager.page_html
        })

    def post(self, request):
        action = request.POST.get('action')
        print(request.POST)
        if not hasattr(self, action):
            return HttpResponse('非法操作')
        getattr(self, action)()

        # return self.get(request)
        return redirect(reverse('customer_list'))
    # 私户转公户
    def multi_public(self):
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).update(consultant=None)

    # 公户转私户
    def multi_apply(self):
        ids = self.request.POST.getlist('id')
        # 方式一
        # models.Customer.objects.filter(id__in=ids).update(consultant=self.request.account)

        # 如果当前有的私户+申请的数量 》 最大值  不允许
        # if self.request.account.customers.all().count() + len(ids) > settings.MAX_CUSTOMER_NUM:
        #     return HttpResponse('做人不能太贪心了')

        # 事务
        with transaction.atomic():
            # 查询出数据加锁
            # 加锁
            queryset = models.Customer.objects.filter(id__in=ids,consultant__isnull=True).select_for_update()

            if len(ids) == queryset.count():
                queryset.update(consultant=self.request.account)
                return
            return HttpResponse('你的挺逗太慢了，已经被别人抢走了')
    def search(self, query_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))
        return q


userlist = [{'name': 'alex-{}'.format(i), 'pwd': "alexdsb-{}".format(i)} for i in range(1, 402)]


def user_list(request):
    # 当前页
    try:
        page = int(request.GET.get('page', '1'))
        if page <= 0:
            page = 1
    except Exception as e:
        page = 1
    print(page)
    # 全部数据
    all_count = len(userlist)
    # 每页显示数据条数
    per_num = 15
    # 总页码数
    page_num, more = divmod(all_count, per_num)
    if more:
        page_num += 1
    start = (page - 1) * per_num
    end = page * per_num
    # 总页码数
    max_show = 11
    half_show = max_show // 2

    # page_start = page - half_show
    # page_end = page + half_show

    if page_num < max_show:
        page_start = 1
        page_end = page_num
    else:
        if page <= half_show:
            page_start = 1
            page_end = max_show
        elif page + half_show > page_num:
            page_start = page_num - max_show + 1
            page_end = page_num
        else:
            page_start = page - half_show
            page_end = page + half_show

    # 返回html
    li_list = []
    if page == 1:
        li_list.append('<li class="disabled" ><a> << </a></li>')
    else:
        li_list.append('<li><a href="?page={}"> << </a></li>'.format(page - 1))

    for i in range(page_start, page_end + 1):
        if page == i:
            li_list.append('<li class="active"><a href="?page={}">{}</a></li>'.format(i, i))
        else:
            li_list.append('<li><a href="?page={}">{}</a></li>'.format(i, i))

    if page == page_num:
        li_list.append('<li class="disabled" ><a> >> </a></li>')
    else:
        li_list.append('<li ><a href="?page={}"> >> </a></li>'.format(page + 1))
    page_html = ''.join(li_list)

    return render(request, 'user_list.html',
                  {'userlist': userlist[start:end],
                   # 'page_num':range(page_start,page_end+1)
                   'page_html': page_html
                   })


def users_lists(request):
    # userlist = [{'name': 'alex-{}'.format(i), 'pwd': "alexdsb-{}".format(i)} for i in range(1, 402)]
    pager = Pagination(request.GET.get('page', '1'), len(userlist), per_num=10, max_show=15)
    print(pager.start, pager.end)
    return render(request, 'user_list.html',
                  {"userlist": userlist[pager.start:pager.end],
                   'page_html': pager.page_html
                   }, )


def customer_add(request):
    form_obj = CustomerForm()
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'customer_add.html', {'form_obj': form_obj})
    # return render(request,'customer_add.html',locals())


def customer_edit(request, edit_id):
    obj = models.Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('customer_list')
    return render(request, 'customer_edit.html', locals())


def customer_change(request, edit_id=None):
    obj = models.Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse_url(request,'customer_list'))
            # return redirect(reverse('customer_list'))
    return render(request, 'customer_change.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 展示跟进记录
def consult_list(request, customer_id):
    if customer_id == '0':
        all_consult = models.ConsultRecord.objects.filter(consultant=request.account)
    else:
        print('customer_id != 0')
        all_consult = models.ConsultRecord.objects.filter(consultant=request.account,customer_id=customer_id)
    return render(request, 'consult_list.html', {'all_consult':all_consult})


# 添加跟进记录
def consult_add(request):
    # 实例化一个包含当前销售的跟进记录
    # form_obj = ConsultForm()
    obj = models.ConsultRecord(consultant=request.account)
    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list', args=('0')))
    return render(request, 'consult_add.html', locals())


# 编辑跟进记录
def consult_edit(request, edit_id):
    obj = models.ConsultRecord.objects.filter(pk=edit_id).first()
    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list', args=('0')))
    return render(request, 'consult_edit.html', locals())


def enrollment_list(request, customer_id):
    if customer_id == '0':
        all_enrollment = models.Enrollment.objects.all()
    else:
        all_enrollment = models.Enrollment.objects.filter(customer_id=customer_id)
    return render(request, 'enrollment_list.html', locals())


def enrollment_add(request, customer_id):
    obj =models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    print('EnrollmentForm')
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('enrollment_list',args=('0')))

    return render(request, 'form.html', locals())

def enrollment_edit(request,record_id):
    obj = models.Enrollment.objects.filter(pk=record_id).first()
    form_obj = EnrollmentForm(instance=obj)
    if request.method == "POST":
        form_obj = EnrollmentForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('enrollment_list',args=('0')))
    return render(request,'form.html',locals())

# 展示班级
class ClassList(View):
    def get(self,request):
        q = self.search([])
        all_class = models.ClassList.objects.filter(q)
        pager = Pagination(request.GET.get('page', '1'), all_class.count(), request.GET.copy(), 10)
        return render(request,'class_list.html',{
            'all_class':all_class[pager.start:pager.end],
            'page_html':pager.page_html
        })

    def post(self,request):
        pass


    def search(self, query_list):
        query = self.request.GET.get('query', '')

        # Q(Q(qq__contains=query) | Q(name__contains=query))
        q = Q()
        q.connector = 'OR'

        #  Q(('qq__contains', query))    Q(qq__contains=query)
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q

# 新增，编辑班级
def classes(request,edit_id=None):
    obj = models.ClassList.objects.filter(pk=edit_id).first()
    form_obj = ClassListForm(instance=obj)
    title = '编辑班级' if edit_id else '添加班级'
    if request.method == 'POST':
        form_obj = ClassListForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('class_list'))
    return render(request,'form.html',{'form_obj':form_obj,'title':title})


# 展示课程记录
class CourseRecordList(View):
    def get(self,request,class_id):
        q = self.search([])
        all_course_record = models.CourseRecord.objects.filter(q,re_class_id=class_id)
        pager = Pagination(request.GET.get('page', '1'), all_course_record.count(), request.GET.copy(), 10)
        # print('pager：',pager.start,pager.end)
        # print('all_course_record:',all_course_record)
        # print('all_course_record[pager.start:pager.end]:',all_course_record[pager.start:pager.end])
        return render(request,'course_record_list.html',{
            'all_course_record':all_course_record[pager.start:pager.end],
            'page_html':pager.page_html,
            'class_id':class_id
        })

    def post(self,request,class_id):
        action = request.POST.get('action')
        if not hasattr(self,action):
            return HttpResponse('非法操作')

        res = getattr(self,action)()
        if res:
            return res
        return self.get(request,class_id)


    def search(self, query_list):
        query = self.request.GET.get('query', '')

        # Q(Q(qq__contains=query) | Q(name__contains=query))
        q = Q()
        q.connector = 'OR'

        #  Q(('qq__contains', query))    Q(qq__contains=query)
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q

    def multi_init(self):
        course_record_ids = self.request.POST.getlist('id')
        course_record_obj_list = models.CourseRecord.objects.filter(id__in=course_record_ids)

        for course_record_obj in course_record_obj_list:
            all_students = course_record_obj.re_class.customer_set.all().filter(status='studying')

            # for student in all_students:
            #     models.StudyRecord.objects.create(course_record=course_record_obj, student=student)

            list1 = []
            for student in all_students:
                list1.append(models.StudyRecord(course_record=course_record_obj,student=student))
            models.StudyRecord.objects.bulk_create(list1)




# 新增，编辑课程
def course_record(request,class_id=None,course_record_id=None):
    if course_record_id:
        obj = models.CourseRecord.objects.filter(pk=course_record_id).first()
    else:
        obj = models.CourseRecord(re_class_id=class_id,teacher=request.account)
        # obj = models.CourseRecord(re_class_id=class_id)
    form_obj = CourseRecordForm(instance=obj)
    title = '新增课程' if class_id else '编辑课程'
    if request.method == 'POST':
        form_obj = CourseRecordForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            # return redirect(reverse('course_record_list',args=(obj.re_class_id if course_record_id else class_id)))
            return redirect(reverse('course_record_list',args=(obj.re_class_id if course_record_id else class_id,)))
    return render(request,'form.html',{'form_obj':form_obj,'title':title})


def study_record(request,course_record_id):
    FormSet = modelformset_factory(models.StudyRecord,StudyRecordForm,extra=0)
    all_study_record = models.StudyRecord.objects.filter(course_record_id=course_record_id)
    form_obj = FormSet(queryset=all_study_record)
    if request.method == 'POST':
        form_obj = FormSet(request.POST,queryset=all_study_record)
        if form_obj.is_valid():
            form_obj.save()
        print(form_obj.errors)
    return render(request,'study_record_list.html',locals())




















