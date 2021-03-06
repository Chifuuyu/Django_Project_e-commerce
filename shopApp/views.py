from datetime import timedelta
import json
import random
from django.utils import timezone
from itertools import chain

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
from .forms import CreateUserForm, orderForm, customerForm
# Create your views here.
from .models import *
from .utils import cartData


def page_not_found_view(request, exception):
    return render(request, 'components/404.html', status=404)


@login_required(login_url='login')
def home(request):
    title = 'Home'

    if request.user.is_superuser:
        orderItems = OrderItem.objects.filter(order__complete=True, order__status='Delivered')
        orders = Order.objects.filter(complete=True)

        weeklySales = OrderItem.objects.filter(order__complete=True, order__status='Delivered',
                                               date_created__range=[timezone.now() -
                                                                    timedelta(days=7),
                                                                    timezone.now()])
        x = 0
        y = 0
        z = 0
        for i in orderItems:
            z += i.get_total
        z = "₱{:0,.2f}".format(z)
        for i in orders:
            y += i.get_cart_items
        for i in weeklySales:
            x += i.get_total
        x = "₱{:0,.2f}".format(x)

        context = {'totalSales': z, 'totalOrders': y, 'weekSales': x, 'orders': orders}
        return render(request, 'admin/home.html', context)

    context = {'tag': Categorie.objects.all(), 'title': title}
    return render(request, 'components/home.html', context)


@login_required(login_url='login')
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    title = 'My Cart'

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'title': title}
    return render(request, 'customer/cart.html', context)


@login_required(login_url='login')
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    title = 'Check Out'

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'title': title}
    return render(request, 'customer/checkout.html', context)


@login_required(login_url='login')
def store(request, category):
    if Categorie.objects.filter(name=category):
        products = Product.objects.filter(tags__name=category)
        title = 'Store/' + category
        context = {'products': products, 'title': title}
        return render(request, 'customer/store.html', context)
    else:
        messages.warning('No category like this')
        return redirect('home')


@login_required(login_url='login')
def product(request, pk):
    productElement = Product.objects.get(id=pk)
    title = 'product/' + productElement.name
    context = {'product': productElement, 'title': title}
    return render(request, 'customer/product.html', context)


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
                messages.success(request,
                                 'added ' + orderItem.product.name + ", " + "Quantity: " + str(orderItem.quantity))
            else:
                orderItem.quantity = value
                messages.success(request,
                                 'added ' + orderItem.product.name + ", " + "Quantity: " + str(orderItem.quantity))
        else:
            if orderItem.quantity < product_item.quantity:
                if orderItem.quantity + value > product_item.quantity:
                    orderItem.quantity = product_item.quantity
                    messages.success(request, 'Updated total of your cart ' + orderItem.product.name + ", "
                                     + "Quantity: " + str(orderItem.quantity))
                else:
                    orderItem.quantity += value
                    messages.success(request, 'Updated total of your cart ' + orderItem.product.name + ", "
                                     + "Quantity: " + str(orderItem.quantity))
            else:
                messages.warning(request, 'Order must not exceed stock limit')

    if action == 'plus':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'minus':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@unauthenticated_user
def register(request):
    title = 'Register'
    form1 = customerForm()
    form2 = CreateUserForm()
    if request.method == 'POST':
        form2 = CreateUserForm(request.POST)
        form1 = customerForm(request.POST)
        if form2.is_valid():
            user = form2.save()
            if form1.is_valid():
                phone = form1.cleaned_data['phone']
                address = form1.cleaned_data['address']
                username = form2.cleaned_data.get('username')
                group = Group.objects.get(name='customer')
                user.groups.add(group)
                x = user.first_name + " " + user.last_name
                Customer.objects.create(
                    user=user,
                    name=x,
                    email=user.email,
                    phone=phone,
                    address=address,
                )
                messages.success(request, 'Account was created for ' + username)
                return HttpResponseRedirect(reverse_lazy('login'))
    context = {'form2': form2, 'title': title, 'form1': form1}
    return render(request, 'components/register.html', context)


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
    return render(request, 'components/login.html', context)


@login_required(login_url='login')
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return HttpResponseRedirect(reverse_lazy('login'))


@login_required(login_url='login')
def confirm_checkout(request):
    bar_code = BarCode
    transaction_id = random.randint(100000000000, 999999999999)
    customer = request.user.customer
    orders, created = Order.objects.get_or_create(customer=customer, complete=False)
    Orders = Order.objects.all()

    try:
        Orders.get(transaction_id=transaction_id)
        transaction_id = random.randint(10000000000, 99999999999)
    except:
        orders.transaction_id = transaction_id
        orders.complete = True
        orders.date_created = timezone.now()
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
    return render(request, 'customer/orders.html', context)


def adminOrderview(request, pk):
    orderitems = OrderItem.objects.filter(order__id=pk)
    orders = Order.objects.filter(id=pk)
    barCode = BarCode.objects.get(order__transaction_id=orders.get(id=pk).transaction_id)
    total = 0
    total_items = 0
    for i in orderitems:
        total += i.get_total
    for i in orders:
        total_items += i.get_cart_items
    orderitems.all()
    context = {'order': orderitems, 'total': total, 'total_items': total_items, 'barcode': barCode}
    return render(request, 'admin/receipt.html', context)


class SearchView(ListView):
    model = Product
    template_name = 'components/search.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        return object_list


class SearchViewForAdmin(ListView):
    model = OrderItem
    template_name = 'admin/search.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        object_list = OrderItem.objects.filter(
            Q(order__customer__name__icontains=query) | Q(order__transaction_id__icontains=query)
        )
        product_list = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        result = chain(object_list, product_list)
        return result


class searchUsingBarcode(ListView):
    model = OrderItem
    template_name = 'admin/searchBarCode.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        search = query[1:-1]
        print(search)

        object_list = OrderItem.objects.filter(
            Q(order__transaction_id__icontains=search)
        )
        updateOrder = Order.objects.get(transaction_id=search)
        updateOrder.status = 'Delivered'
        updateOrder.save()
        messages.success(self.request, 'Update Successfully')
        return object_list


def updateDelivery(request, pk):
    orderItems = OrderItem.objects.filter(order__complete=True, order__status='Delivered')
    weeklySales = OrderItem.objects.filter(order__complete=True, order__status='Delivered',
                                           date_created__range=[timezone.now() -
                                                                timedelta(days=7),
                                                                timezone.now()])

    orderItem = Order.objects.get(id=pk)
    orders = Order.objects.filter(complete=True)
    form = orderForm(instance=orderItem)
    dateToday = timezone.now()
    x = 0
    y = 0
    z = 0
    for i in orderItems:
        z += i.get_total
    z = "₱{:0,.2f}".format(z)
    for i in orders:
        y += i.get_cart_items
    for i in weeklySales:
        x += i.get_total
    x = "₱{:0,.2f}".format(x)

    if request.method == 'POST':
        form = orderForm(request.POST, instance=orderItem)
        print('true')
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated')
            print('WORKING')
            return redirect('home')
        else:
            print('not working')

    context = {'totalSales': z, 'totalOrders': y, 'weekSales': x, 'orders': orders, 'dateToday': dateToday,
               'form': form}
    return render(request, 'admin/home.html', context)
