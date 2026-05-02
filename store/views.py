from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm, RegisterForm
import razorpay
from django.conf import settings

# Initialize Razorpay Client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def home(request):
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    featured = Product.objects.filter(is_active=True, stock__gt=0)[:4]
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'featured': featured,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search_q = request.GET.get('q', '')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    if search_q:
        products = products.filter(Q(name__icontains=search_q) | Q(description__icontains=search_q))

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_q': search_q,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
    })


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'"{product.name}" added to your cart!')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty > 0:
        cart_item.quantity = qty
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    # This handles the final form submission AFTER payment is done via JS
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        payment_id = request.POST.get('razorpay_payment_id')

        if form.is_valid() and payment_id:
            # Create the final order in your database
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data["shipping_address"],
                phone=form.cleaned_data["phone"],
                notes=form.cleaned_data.get('notes', ''),
                status='Paid' # Set status to paid immediately
            )
            
            # Transfer items from Cart to Order
            for item in cart.cart_items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            
            # Clear the cart
            cart.cart_items.all().delete()
            
            messages.success(request, f"Order #{order.id} placed successfully!")
            return redirect("order_detail", order_id=order.id)
    
    # --- THIS PART RUNS WHEN THE USER FIRST OPENS THE CHECKOUT PAGE ---
    else:
        form = CheckoutForm(initial={
            'shipping_address': request.user.profile.address if hasattr(request.user, 'profile') else '',
        })

    # 1. Calculate amount in Paise
    # Use float(cart.total) if total is a Decimal
    amount_paise = int(cart.total * 100) 

    # 2. Pre-create the Razorpay Order so the ID is ready for the JS Popup
    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    # 3. Pass everything to the template
    context = {
        "cart": cart, 
        "form": form,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID, # Now JS will see the key!
        "amount": amount_paise,
    }

    return render(request, "store/checkout.html", context)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')
