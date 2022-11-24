import datetime
from django import http
from django.http import HttpResponse, HttpResponseRedirect
import csv
from django.shortcuts import redirect, render
from Loginsys.models import newuser
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.views import View
from pprint import pprint
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import csv
import xlwt
from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile
from django.db.models import Sum

from django.template.loader import render_to_string
import tempfile
from django.db.models import Sum


def Indexpage(request):
    return render(request, 'index.html')


def Homepage(request):
    users = newuser.objects.all()
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    usersfinal = paginator.get_page(page_number)
    totalpage = usersfinal.paginator.num_pages

    data={
        'users': usersfinal,
        'lastpage': totalpage,
        'totalPagelist': [n+1 for n in range(totalpage)],
    }
    return render(request,'home.html',data)

def Signuppage(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        gender=request.POST['gender']

        #validation
        error_message = None
        if(not name):
            error_message = "Name Field is Required"
        elif not email:
            error_message = "Email Required"
        elif password!=cpassword:
            error_message= "Passowrd Does not match"
        
        #Saving
        if not error_message:
            newuser(name=name, email=email, password=password, gender=gender)
            customer = newuser(name=name, email=email, password=password, gender=gender)
            customer.password=make_password(customer.password)
            customer.save()
            
            messages.success(request,'The New User ' + request.POST['name']+" is saved successfully.")
            return render (request,'signup.html')
        else:
            return render (request,'signup.html', {'error' : error_message} )
    else:
        return render(request,'signup.html')


def Loginpage(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:   
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = newuser.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password,customer.password)
            if flag:
                return render(request,'home.html')
            else:
                error_message = 'Password Invalid!!'
        else:
            error_message = 'Email invalid!'
            print(email,password)
            return render(request,'login.html', {'error': error_message})



def Logoutpage(request):
    try:
        del request.session['email']
    except:
        return render(request, 'index.html')
    return render(request, 'index.html')


def export_csv(request):
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['name', 'email', 'gender'])

    rows= newuser.objects.all().values_list('name', 'email', 'gender')
    for data in rows:
        writer.writerow([data.name, data.email, data.gender])
    return response

def export_excel(request):
    response=HttpResponse(content_type='application/ms-excel') #This will handle the type of file
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.xls'

    #Now Creating Workbook
    wb = xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('UserData')
    row_num = 0
    font_style=xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['name', 'email', 'gender']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    rows = newuser.objects.all().values_list('name', 'email', 'gender')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def export_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.pdf'
    response['Content-Transfer_Encoding'] = 'binary'

    html_string=render_to_string('pdf-output.html',{'usersdata':[], 'total':0})

    html=HTML(string=html_string)

    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output=open(output.name,'rb') --> This statements is giving permission denied error.Therefore we are using output.seek(0)
        output.seek(0) 
        response.write(output.read())
    return response

    