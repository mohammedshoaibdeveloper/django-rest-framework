from re import A
from tkinter import SE
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from django.conf import settings
import Api.usable as uc
from .models import *
from passlib.hash import django_pbkdf2_sha256 as handler
import jwt 
import datetime
from decouple import config
from django.db.models import F

# Create your views here.
### ADMIN AND USER LOGIN
class login(APIView):
     def post(self,request):
         requireFields = ['email','password']
         validator = uc.keyValidation(True,True,request.data,requireFields)
            
         if validator:
            return Response(validator,status = 200)
            
         else:
               email = request.data.get('email')
               password = request.data.get('password')
               fetchAccount = Account.objects.filter(email=email).first()
               if fetchAccount:
                  if handler.verify(password,fetchAccount.password):
                     if fetchAccount.role == 'admin':
                        access_token_payload = {
                              'id':str(fetchAccount.uid),
                              'firstname':fetchAccount.firstname, 
                              'email':fetchAccount.email, 
                              'exp': datetime.datetime.utcnow() + datetime.timedelta(days=22),
                              'iat': datetime.datetime.utcnow(),

                           }

                        
                        access_token = jwt.encode(access_token_payload,config('adminkey'),algorithm = 'HS256')
                        data = {'uid':fetchAccount.uid,'firstname':fetchAccount.firstname,'lastname':fetchAccount.lastname,'email':fetchAccount.email,'contactno':fetchAccount.contactno,'role':fetchAccount.role}

                        whitelistToken(user = fetchAccount,token = access_token,useragent = request.META['HTTP_USER_AGENT'],created_at = datetime.datetime.now()).save()

                        
                        return Response({"status":True,"message":"Login Successlly","token":access_token,"admindata":data})

                     else:
                        access_token_payload = {
                              'id':str(fetchAccount.uid),
                              'firstname':fetchAccount.firstname, 
                              'email':fetchAccount.email, 
                              'exp': datetime.datetime.utcnow() + datetime.timedelta(days=22),
                              'iat': datetime.datetime.utcnow(),

                           }

                        
                        access_token = jwt.encode(access_token_payload,config('customerkey'),algorithm = 'HS256')
                        data = {'uid':fetchAccount.uid,'firstname':fetchAccount.firstname,'lastname':fetchAccount.lastname,'email':fetchAccount.email,'contactno':fetchAccount.contactno,'role':fetchAccount.role}

                        whitelistToken(user = fetchAccount,token = access_token,useragent = request.META['HTTP_USER_AGENT'],created_at = datetime.datetime.now()).save()

                        
                        return Response({"status":True,"message":"Login Successlly","token":access_token,"custumerdata":data})
                  else:
                     return Response({"status":False,"message":"Invalid Creadientials"})
               else:
                  return Response({"status":False,"message":"Invalid Creadientials"})
          
               
### PASSWORD ENCRYPTED

class encryptpass(APIView):
    def post(self,request):
        try:    
            passw = handler.hash(request.data.get('passw'))


            return HttpResponse(passw)

        except Exception as e:
            
            message = {'status':'Error','message':str(e)}
            return Response(message)

### CATEGORY ADD
class categoryAdd(APIView):

### CATEGORY ADD
   def post(self,request):
      requireFields = ['name','description']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            name  = request.data.get('name')
            description = request.data.get('description')
            
            access = Category.objects.filter(name = name ).first()
            if access:
               return Response({"status":False,"message":"Category Name Already Exist"})
               
            data = Category(name = name, description = description)
            data.save()

            return Response ({"status":True,"message":"Category Successlly Add"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})


### CATEGORY GET
class Getcategory(APIView):
   def get (self,request):
      my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
      if my_token:
         data = Category.objects.all().values('uid','name','description').order_by("-created_at")
         return Response ({"status":True,"data":data })
      else:
         return Response ({"status":False,"message":"Unauthorized"})


### CATEGORY UPDATE
class Editcategory(APIView):
   def put (self,request):
      requireFields = ['uid','name','description']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.data.get('uid')

            checkcategory= Category.objects.filter(uid = uid).first()

            if checkcategory:
               checkcategory.name = request.data.get('name') 
               checkcategory.description = request.data.get('description') 

               checkcategory.save()
               return Response({"status":True,"message":"Category Updated Successfully"})
            else:
               return Response({"status":True,"message":"Data not found"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})


### CATEGORY DELETE 
class deletecategory(APIView):
   def delete(self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.GET['uid']
            data = Category.objects.filter(uid = uid).first()
            if data:
               data.delete()
               return Response({"status":True,"message":"Data Deleted Successfully"})
            else:
               return Response({"status":False,"message":"Data not found"})


###  GET SPECIFIC CATEGORY 
class Getspecificcategory(APIView):
   def get(self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
               uid = request.GET['uid']
               data = Category.objects.filter(uid = uid).values("uid","name",'description').first()
               if data:
                  return Response({"status":True,"data":data},200)
               else:
                  return Response({"status":False,"message":"Data not found"})


### ADMIN ADD LOGO

class Addlogo(APIView):
    def post (self,request):
        requireFields = ['image']
        validator = uc.keyValidation(True,True,request.data,requireFields)
                
        if validator:
            return Response(validator,status = 200)
                
        else:
            my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
            if my_token:
                image  = request.data.get('image')
                
                data = logo(image = image)
                data.save()

                return Response ({"status":True,"message":"logo Successlly Add"})

            else:
                return Response ({"status":False,"message":"Unauthorized"})


### LOGO GET
class Getlogo(APIView):
   def get (self,request):
      my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
      if my_token:
         data = logo.objects.all().values('uid','image').order_by("-created_at")
         return Response ({"status":True,"data":data })
      else:
         return Response ({"status":False,"message":"Unauthorized"})



### LOGO UPDATE
class Editlogo(APIView):
   def put (self,request):
      requireFields = ['uid','image']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.data.get('uid')

            checkclogo= logo.objects.filter(uid = uid).first()

            if checkclogo:
               checkclogo.image = request.data.get('image') 


               checkclogo.save()
               return Response({"status":True,"message":"Logo Edit Successfully"})
            else:
               return Response({"status":True,"message":"Data not found"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})



### DELETE LOGO  
class deletelogo(APIView):
   def delete(self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.GET['uid']
            data = logo.objects.filter(uid = uid).first()
            if data:
               data.delete()
               return Response({"status":True,"message":"Data Deleted Successfully"})
            else:
               return Response({"status":False,"message":"Data not found"})



###  GET SPECIFIC LOGO 
class Getspecificlogo(APIView):
   def get(self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
               uid = request.GET['uid']
               data = logo.objects.filter(uid = uid).values("uid","image").first()
               if data:
                  return Response({"status":True,"data":data},200)
               else:
                  return Response({"status":False,"message":"Data not found"})

###  ADD SLIDER 
class addSlider(APIView):
    def post(self, request):
        requireFields = ['image','categoryid']
        validator = uc.keyValidation(True,True,request.data,requireFields)
                
        if validator:
            return Response(validator,status = 200)
                
        else:
            my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
            if my_token:
                image = request.data.getlist('image')
                categoryid = request.data.get('categoryid')

                getcategory = Category.objects.filter(uid = categoryid).first()

                for i in range(len(image)):

                    imageObj = Slider(categoryid = getcategory,image =image[i]  )
                    imageObj.save()
                return Response({"status":True,"message":"Slider image  successfully"})
            else:
                return Response({"status":False,"message":"Unauthorized"})


###  GET SLIDER 
class getSliderImages(APIView):
    def get(self,request):
        my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
        if my_token:
            data = Slider.objects.all().values('uid','image',CategoryName=F('categoryid__name')).order_by("-created_at")
            print(data)
            for i in range(len(data)):

                mydata = Slider.objects.filter(categoryid = data[i]['uid']).values('image').first()
                if mydata:
                
                    data[i]['Slider'] = mydata['image']
                    
                else:
                    return Response ({"status":True,"data":data })
        else:
            return Response ({"status":False,"message":"Unauthorized"})

###  DELETE SLIDER 
class DeleteSlider(APIView):
   def delete (self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.GET['uid']
            data = Slider.objects.filter(uid = uid).first()
            if data:
               data.delete()
               return Response({"status":True,"message":"Data Deleted Successfully"})
            else:
               return Response({"status":False,"message":"Data not found"})

###  GET SPECIFIC SLIDER 
class GetSpecificSliderImage(APIView):
   def get (self, request):
         requireFields = ['uid']
         validator = uc.keyValidation(True,True,request.GET,requireFields)
               
         if validator:
            return Response(validator,status = 200)
               
         else:
            my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
            if my_token:
                  uid = request.GET['uid']
                  data = Slider.objects.filter(uid = uid).values("uid","image",'categoryid').first()
                  if data:
                     return Response({"status":True,"data":data},200)
                  else:
                     return Response({"status":False,"message":"Data not found"})


###  ADD NAVBAR
class Addnavbar(APIView):
   def post (self,request):
      requireFields = ['name']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            name = request.data.get('name')

            access = navbar.objects.filter(name = name ).first()
            if access:
               return Response({"status":False,"message":"Category Name Already Exist"})
               
            data = navbar(name = name)
            data.save()

            return Response ({"status":True,"message":"Category Successlly Add"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})

###  GET NAVBAR
class GetNavbar(APIView):
   def get(self, request):
      my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
      if my_token:
         data = navbar.objects.all().values('uid','name').order_by("-created_at")
         return Response ({"status":True,"data":data })
      else:
         return Response ({"status":False,"message":"Unauthorized"})

###  EDIT NAVBAR
class EditNavbar(APIView):
   def put (self,request):
      requireFields = ['uid','name']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.data.get('uid')

            checknavbar= navbar.objects.filter(uid = uid).first()
            if checknavbar:
               checknavbar.name = request.data.get('name') 

               checknavbar.save()
               return Response({"status":True,"message":"Category Updated Successfully"})
            else:
               return Response({"status":True,"message":"Data not found"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})

###  DELETE NAVBAR
class deleteNavbar(APIView):
   def delete (self,request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.GET['uid']
            data = navbar.objects.filter(uid = uid).first()
            if data:
               data.delete()
               return Response({"status":True,"message":"Data Deleted Successfully"})
            else:
               return Response({"status":False,"message":"Data not found"})

###  GET SPECIFIC NAVBAR
class GetSpecificNavbar(APIView):
   def get(self, request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
               uid = request.GET['uid']
               data = navbar.objects.filter(uid = uid).values("uid","name").first()
               if data:
                  return Response({"status":True,"data":data},200)
               else:
                  return Response({"status":False,"message":"Data not found"})

### ADD SECTION
class AddSection(APIView):
   def post (self,request):
      requireFields = ['mainheading','subheading','maindescription','shortdescription','icon','categoryid']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
         
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            mainheading = request.data.get('mainheading')
            subheading = request.data.get('subheading')
            maindescription = request.data.get('maindescription')
            shortdescription = request.data.get('shortdescription')
            icon = request.data.get('icon')
            categoryid = request.data.get('categoryid')

            getcategory = Category.objects.filter(name = categoryid).first()
               
            data = Section(mainheading = mainheading,subheading = subheading,maindescription= maindescription,shortdescription = shortdescription ,icon =  icon,categoryid= getcategory)
            data.save()

            return Response ({"status":True,"message":"Section Successlly Add"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})

### GET SECTION
class GetSections(APIView):
   def get (self, request):
      my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
      if my_token:
         data = Section.objects.all().values('uid','mainheading','subheading','maindescription','shortdescription','icon','categoryid').order_by("-created_at")
         return Response ({"status":True,"data":data })
      else:
         return Response ({"status":False,"message":"Unauthorized"})

### EDIT SECTION
class EditSection(APIView):
   def put (self,request):
      requireFields = ['uid','mainheading','subheading','maindescription','shortdescription','icon']
      validator = uc.keyValidation(True,True,request.data,requireFields)
            
      if validator:
         return Response(validator,status = 200)
         
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.data.get('uid')

            checksection= Section.objects.filter(uid = uid).first()

            if checksection:
               checksection.mainheading = request.data.get('mainheading') 
               checksection.subheading = request.data.get('subheading') 
               checksection.subheading = request.data.get('subheading') 
               checksection.maindescription = request.data.get('maindescription') 
               checksection.shortdescription = request.data.get('shortdescription') 
               checksection.icon = request.data.get('icon') 

               checksection.save()
               return Response({"status":True,"message":"Category Updated Successfully"})
            else:
               return Response({"status":True,"message":"Data not found"})

         else:
            return Response ({"status":False,"message":"Unauthorized"})

### DELETE SECTION
class deleteSections(APIView):
   def delete (self, request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
            uid = request.GET['uid']
            data = Section.objects.filter(uid = uid).first()
            if data:
               data.delete()
               return Response({"status":True,"message":"Data Deleted Successfully"})
            else:
               return Response({"status":False,"message":"Data not found"})

### GET SECTION
class GetspecificSections(APIView):
   def get(self, request):
      requireFields = ['uid']
      validator = uc.keyValidation(True,True,request.GET,requireFields)
            
      if validator:
         return Response(validator,status = 200)
            
      else:
         my_token = uc.admintokenauth(request.META['HTTP_AUTHORIZATION'][7:])
         if my_token:
               uid = request.GET['uid']
               data = Section.objects.filter(uid = uid).values('uid','mainheading','subheading','maindescription','shortdescription','icon','categoryid').first()
               if data:
                  return Response({"status":True,"data":data},200)
               else:
                  return Response({"status":False,"message":"Data not found"})
