import json
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView

from .decorators import *
from .forms import CreateUserForm
# Create your views here.
from .models import *
from .utils import cartData


@login_required(login_url='login')
def home(request):
    title = 'Home'
    context = {'tag': Tag.objects.all(), 'title': title}

    return render(request, 'home.html', context)


@login_required(login_url='login')
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    title = 'My Cart'

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'title': title}
    return render(request, 'cart.html', context)


@login_required(login_url='login')
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    title = 'Check Out'

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'title': title}
    return render(request, 'checkout.html', context)


@login_required(login_url='login')
def store(request, category):
    if Tag.objects.filter(name=category):
        products = Product.objects.filter(tags__name=category)
        title = 'Store/' + category
        context = {'products': products, 'title': title}
        return render(request, 'store.html', context)
    else:
        messages.warning('No category like this')
        return redirect('home')


@login_required(login_url='login')
def product(request, pk):
    productElement = Product.objects.get(id=pk)
    title = 'product/' + productElement.name
    context = {'product': productElement, 'title': title}
    return render(request, 'product.html', context)


@login_required(login_url='login')
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    value = data['value']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product_item = Product.objects.get(id=productId)
    orders, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=orders, product=product_item)

    if action == 'add':
        if orderItem.quantity is None:
            if value > product_item.quantity:
                orderItem.quantity = product_item.quantity
                messages.success(request, 'added ' + orderItem.product.name + ", " + "Quantity: " + str(orderItem.quantity))
            else:
                orderItem.quantity = value
                messages.success(request, 'added ' + orderItem.product.name + ", " + "Quantity: " + str(orderItem.quantity))
        else:
            if orderItem.quantity < product_item.quantity:
                if value > product_item.quantity:
                    orderItem.quantity = product_item.quantity
                    messages.success(request, 'Updated total of your cart ' + orderItem.product.name + ", "
                                     + "Quantity: " + str(orderItem.quantity))
                else:
                    orderItem.quantity += value
                    messages.success(request, 'Updated total of your cart ' + orderItem.product.name + ", "
                                     + "Quantity: " + str(orderItem.quantity))
            else:
                messages.warning('Order must not exceed stock limit')

    if action == 'plus':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'minus':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    if orderItem is None:
        print('true')
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@unauthenticated_user
def register(request):
    title = 'Register'
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            x = user.first_name + " " + user.last_name
            Customer.objects.create(
                user=user,
                name=x,
                email=user.email,

            )
            messages.success(request, 'Account was created for ' + username)
            return HttpResponseRedirect(reverse_lazy('login'))
    context = {'form': form, 'title': title}
    return render(request, 'register.html', context)


@unauthenticated_user
def loginPage(request):
    title = 'Login'
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'Username OR password is incorrect')

    context = {'title': title}
    return render(request, 'login.html', context)


@login_required(login_url='login')
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return HttpResponseRedirect(reverse_lazy('login'))


"""def orderInfo(request, pk):
    order = Order.objects.get(id=pk)
    custName = order.customer.name
    prodName = order.product.name
    orderPrice = order.product.price
    ordStatus = order.status
    generated_bCode = order.barcode.image

    context = {'custName': custName, 'prodName': prodName, 'ordStatus': ordStatus, 'orderPrice': orderPrice,
               'orderId': order.id, 'generated_bCode': generated_bCode}
    return render(request, '', context)"""


@login_required(login_url='login')
def confirm_checkout(request):
    bar_code = BarCode
    transaction_id = random.randint(10000000000, 99999999999)
    customer = request.user.customer
    orders, created = Order.objects.get_or_create(customer=customer, complete=False)
    Orders = Order.objects.all()

    try:
        Orders.get(transaction_id=transaction_id)
        transaction_id = random.randint(10000000000, 99999999999)
    except:
        orders.transaction_id = transaction_id
        orders.complete = True
        orders.save()
        bar_code.objects.create(
            order_id=orders.id,
        )

    orderItems = OrderItem.objects.filter(order__transaction_id=orders.transaction_id)
    products = Product.objects.all()
    for i in orderItems:
        x = i.product_id
        y = products.get(id=x)
        z = y.quantity - i.quantity
        y.quantity = z
        y.save()

    messages.info(request, "Ordered Successfully")
    return HttpResponseRedirect(reverse_lazy('home'))


@login_required(login_url='login')
def order(request):
    customer = request.user.customer
    orders = OrderItem.objects.filter(order__customer=customer, order__complete=True)
    orders.all()
    title = 'My Orders'
    context = {'orders': orders, 'title': title}
    return render(request, 'orders.html', context)


class SearchView(ListView):
    model = Product
    template_name = 'components/search.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        return object_list
