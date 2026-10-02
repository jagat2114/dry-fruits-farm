from decimal import Decimal 
 
from django.shortcuts import get_object_or_404, redirect, render 
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User 
 
from .models import Product, Order, OrderItem 
 
 
@login_required(login_url='store:login') 
def home(request): 
    products = Product.objects.filter(available=True)[:6] 
 
    return render( 
        request, 
        'store/home.html', 
        {'products': products} 
    ) 
 
 
def product_list(request): 
    products = Product.objects.all() 
 
    search = request.GET.get('search', '') 
    category = request.GET.get('category', '') 
 
    if search: 
        products = products.filter(name__icontains=search) 
 
    if category: 
        products = products.filter(category=category) 
 
    return render( 
        request, 
        'store/product_list.html', 
        { 
            'products': products, 
            'search': search, 
            'category': category, 
        } 
    ) 
 
def product_detail(request, slug): 
    product = get_object_or_404( 
        Product, 
        slug=slug, 
        available=True 
    ) 
 
    return render( 
        request, 
        'store/product_detail.html', 
        {'product': product} 
    ) 
 
 
def cart_add(request, product_id): 
    product = get_object_or_404( 
        Product, 
        id=product_id, 
        available=True 
    ) 
 
    cart = request.session.get('cart', {}) 
    product_key = str(product.id) 
 
    current_quantity = cart.get(product_key, 0) 
 
    if current_quantity >= product.stock: 
        return redirect('store:cart_detail') 
 
    cart[product_key] = current_quantity + 1 
 
    request.session['cart'] = cart 
    request.session.modified = True 
 
    return redirect('store:cart_detail') 
 
def cart_increase(request, product_id): 
    cart = request.session.get('cart', {}) 
    product_key = str(product_id) 
 
    if product_key in cart: 
        product = get_object_or_404( 
            Product, 
            id=product_id, 
            available=True 
        )  
 
        if cart[product_key] < product.stock: 
            cart[product_key] += 1 
 
    request.session['cart'] = cart 
    request.session.modified = True 
 
    return redirect('store:cart_detail') 
 
 
def cart_decrease(request, product_id): 
    cart = request.session.get('cart', {}) 
    product_key = str(product_id) 
 
    if product_key in cart: 
        cart[product_key] -= 1 
 
        if cart[product_key] <= 0: 
            del cart[product_key] 
 
    request.session['cart'] = cart 
    return redirect('store:cart_detail') 
 
 
def cart_remove(request, product_id): 
    cart = request.session.get('cart', {}) 
    product_key = str(product_id) 
 
    if product_key in cart: 
        del cart[product_key] 
 
    request.session['cart'] = cart 
    return redirect('store:cart_detail') 
 
 
def cart_detail(request): 
    cart = request.session.get('cart', {}) 
    products = Product.objects.filter( 
        id__in=cart.keys(), 
        available=True 
    ) 
 
    items = [] 
    total = Decimal('0.00') 
 
    for product in products: 
        quantity = cart.get(str(product.id), 0) 
        subtotal = product.price * quantity 
        total += subtotal 
 
        items.append({ 
            'product': product, 
            'quantity': quantity, 
            'subtotal': subtotal 
        }) 
 
    return render( 
        request, 
        'store/cart.html', 
        { 
            'items': items, 
            'total': total 
        } 
    ) 
 
@login_required(login_url='store:login')
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('store:cart_detail')

    items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(
            Product,
            id=product_id,
            available=True
        )

        quantity = int(quantity)

        if quantity > product.stock:
            return redirect('store:cart_detail')

        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        if customer_name and mobile and address:

            order = Order.objects.create(
                user=request.user,
                customer_name=customer_name,
                mobile=mobile,
                address=address,
                total_amount=total
            )

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    price=item['product'].price,
                    quantity=item['quantity']
                )

                item['product'].stock -= item['quantity']
                item['product'].save()

            request.session['cart'] = {}
            request.session.modified = True

            return redirect(
                'store:order_success',
                order_id=order.id
            )

    return render(
        request,
        'store/place_order.html',
        {
            'items': items,
            'total': total,
        }
    )

@login_required(login_url='store:login') 
def order_success(request, order_id): 
    order = get_object_or_404( 
        Order, 
        id=order_id, 
        user=request.user 
    ) 
 
    return render( 
        request, 
        'store/order_success.html', 
        { 
            'order': order 
        } 
    ) 
 
@login_required(login_url='store:login') 
def my_orders(request): 
    orders = Order.objects.filter( 
        user=request.user 
    ).order_by('-created_at') 
 
    return render( 
        request, 
        'store/my_orders.html', 
        { 
            'orders': orders 
        } 
    ) 
 
@login_required(login_url='store:login') 
def order_detail(request, order_id): 
    order = get_object_or_404( 
        Order, 
        id=order_id, 
        user=request.user 
    ) 
 
    return render( 
        request, 
        'store/order_detail.html', 
        { 
            'order': order 
        } 
    ) 
 
@login_required(login_url='store:login') 
def cancel_order(request, order_id): 
    order = get_object_or_404( 
        Order, 
        id=order_id, 
        user=request.user 
    ) 
 
    if request.method == 'POST' and order.status == 'pending': 
        order.delete() 
 
    return redirect('store:my_orders') 
 
def login_view(request): 
    if request.method == 'POST': 
        username = request.POST.get('username') 
        password = request.POST.get('password') 
 
        user = authenticate( 
            request, 
            username=username, 
            password=password 
        ) 
 
        if user is not None: 
            login(request, user) 
            return redirect('store:home') 
 
        return render( 
            request, 
            'store/login.html', 
            { 
                'error': 'Invalid username or password' 
            } 
        ) 
 
    return render(request, 'store/login.html') 
 
 
def register_view(request): 
    if request.method == 'POST': 
        username = request.POST.get('username') 
        password = request.POST.get('password') 
 
        if User.objects.filter(username=username).exists(): 
            return render( 
                request, 
                'store/register.html', 
                { 
                    'error': 'Username already exists' 
                } 
            ) 
 
        user = User.objects.create_user( 
            username=username, 
            password=password 
        ) 
 
        login(request, user) 
 
        return redirect('store:home') 
 
    return render(request, 'store/register.html') 
 
 
def logout_view(request): 
    logout(request) 
    return redirect('store:login') 
  