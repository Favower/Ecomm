from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Cart, Product, Customer
from .forms import CustomerRegistrationForm, LoginForm, MyPasswordResetForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q


def home(request):
    return render(request, "myapp/home.html")

def about(request):
    return render(request, "myapp/about.html")

def contact(request):
    return render(request, "myapp/contact.html")


class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "myapp/category.html", locals())


class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "myapp/category.html", locals())

class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request,"myapp/productdetail.html", locals())
    
class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'myapp/customerregistration.html', locals())
    
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Ура! Вы создали учетную запись успешно.")
        else:
            messages.warning(request, "Попробуйте повторить, введены некорректные данные")
        return render(request, 'myapp/customerregistration.html', locals())
    

class PasswordResetView(MyPasswordResetForm):
    pass


class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,'myapp/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name     = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city     = form.cleaned_data['city']
            mobile   = form.cleaned_data['mobile']
            state    = form.cleaned_data['state']
            zipcode  = form.cleaned_data['zipcode']
            

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Успешно добавлены данные")
        else:
            messages.warning(request,"Данные введены неверно")
        return render(request, 'myapp/profile.html', locals())
    


def address (request) :
        add = Customer.objects.filter(user=request.user)
        return render(request, 'myapp/address.html', locals())


class UpdateAddress(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'myapp/updateaddress.html',locals())

    def post(self, request, pk ):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Поздравляем профиль обновлен")
        else:
            messages.warning(request,"Неверно введены данные")
        return redirect("address")
    
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    print(f"Received product_id: {product_id}")
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect("/cart")

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40
    return render(request, 'myapp/addtocart.html', locals())


class Checkout(View):
    def get(self, request):
        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        return render(request, 'myapp/checkout.html', locals())
    

def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if cart_items.exists():
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()

            cart = Cart.objects.filter(user=request.user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount += value
            totalamount = amount + 40
            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        
    return JsonResponse({}, status=400)  # Ответ с ошибкой, если что-то пошло не так

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if cart_items.exists():
            cart_item = cart_items.first()
            cart_item.quantity -= 1
            cart_item.save()

            cart = Cart.objects.filter(user=request.user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount += value
            totalamount = amount + 40
            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        
    return JsonResponse({}, status=400)  # Ответ с ошибкой, если что-то пошло не так

    

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        cart_items = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user))
        
        if cart_items.exists():
            cart_item = cart_items.first()
            cart_item.delete()

            cart = Cart.objects.filter(user=request.user)
            amount = 0
            for p in cart:
                value = p.quantity * p.product.discounted_price
                amount += value
            totalamount = amount + 40
            data = {
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            }
            return JsonResponse(data)
        
    return JsonResponse({}, status=400)  # Ответ с ошибкой, если что-то пошло не так