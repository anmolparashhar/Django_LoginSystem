import datetime
from decimal import ROUND_UP, Rounded
from tkinter import ROUND
from django import http
from django.http import HttpResponse, HttpResponseRedirect
import csv
from django.shortcuts import redirect, render
from . models import newuser
import mysql.connector as sql
from operator import itemgetter #to get the email and password
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from pprint import pprint
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import csv
import xlwt
from weasyprint import HTML
from django.template.loader import render_to_string
import tempfile
from . decorators import login_is_required
from django.db.models import Sum

def Indexpage(request):
    return render(request, 'index.html')

@login_is_required()
def Homepage(request):
        cust = newuser.objects.all().values()
        users = newuser.objects.all()
        paginator = Paginator(users, 5)
        page_number = request.GET.get('page')
        usersfinal = paginator.get_page(page_number)
        totalpage = usersfinal.paginator.num_pages
        totalsum = newuser.objects.all().aggregate(total=Sum('expenses'))

        data={
            'tsum' : totalsum,
            'luser_id': request.session.get('customer_id'),
            'luser_email': request.session.get('customer_email'),
            'luser_name' : request.session.get('customer_name'),
            'udata': cust,
            'users': usersfinal,
            'lastpage': totalpage,
            'totalPagelist': [n+1 for n in range(totalpage)],
        }
        return render (request, 'home.html',data)



def Signuppage(request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        gender=request.POST['gender']
        expenses=request.POST['expenses']
        #validation
        error_message = None
        if(not name):
            error_message = "Name Field is Required"
        elif not email:
            error_message = "Email Required"
        elif password!=cpassword:
            error_message= "Passowrd Does not match"

        if not error_message:
            ruser = newuser(name=name, email=email, password=password, cpassword=cpassword, gender=gender, expenses=expenses)           
            messages.success(request,'The New User ' + request.POST['name']+" is saved successfully.")
            ruser.password=make_password(ruser.password)
            ruser.save()
            return redirect(Signuppage)
    else:
        return render(request,'signup.html')

def Loginpage(request):
    if request.method=="GET":
        return render(request, "login.html")
    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        luser = newuser.get_user_by_email(email)
        error_message=""
        if luser:
            match_password = check_password(password, luser.password)
            if match_password:
                request.session['customer_id'] = luser.id
                request.session['customer_email'] = luser.email
                request.session['customer_name'] = luser.name
                if request.GET.get('next', None):
                    return HttpResponseRedirect(request.GET['next'])
                return redirect(Homepage)
            else:
                error_message='Invalid Password'
                return render(request,'login.html',{'error': error_message})
        else:
            error_message = 'Invalid Email, Please register first.'
            return render(request,'login.html', {'error': error_message})
            
    else:
        return render(request,'login.html')


def Logoutpage(request):
    try:
        del request.session['customer_email']
    except:
        return HttpResponse('Something went wrong')
    return render(request, 'index.html')


def export_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['name', 'email', 'gender', 'expenses'])

    userscsv = newuser.objects.all()
    csvsum = newuser.objects.all().aggregate(tcsv=Sum('expenses'))

    # Get all data from UserDetail Databse Table
    users = newuser.objects.all()
    for data in users:
        writer.writerow([data.name, data.email, data.gender, data.expenses])
    return response

def export_excel(request):
    response=HttpResponse(content_type='application/ms-excel') #This will handle the type of file
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.xls'

    #Now Creating Workbook
    wb = xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('UserData') # this will make a sheet named UsersData
    row_num = 0
    font_style=xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['name', 'email', 'gender', 'expenses']
    for col_num in range(len(columns)): 
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    rows = newuser.objects.all().values_list('name', 'email', 'gender', 'expenses')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

def export_pdf(request):
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment; filename=UsersData'+str(datetime.datetime.now())+'.pdf'
    # If we write inline; here then it will open the file in browser first then we can download from there. 
    #If we do not write inline it will directly download the file
    response['Content-Transfer_Encoding'] = 'binary'

    # Get all data from UserDetail Databse Table
    usersdata = newuser.objects.all()
    pdfsum = newuser.objects.all().aggregate(tpdf=Sum('expenses'))

    html_string=render_to_string('pdf-output.html',{'usersdata':usersdata, 'pdf': pdfsum, 'total':0})
    #if the pdf_output.html is in folder in templates then we will write 'foldername/pdf-output.html'

    html=HTML(string=html_string)

    result = html.write_pdf()
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        #output=open(output.name,'rb') --> This statements is giving permission denied error.Therefore we are using output.seek(0)
        output.seek(0) 
        response.write(output.read())
    return response

    