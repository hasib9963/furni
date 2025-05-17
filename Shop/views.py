from django.shortcuts import render, redirect, get_object_or_404
from Shop.models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
# Create your views here.

def shop(request):
    data = Product.objects.all()
    return render(request, 'shop.html', {'data': data})



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    next_url = request.GET.get('next', 'shop')  # Default to 'shop' if no next URL is provided

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("AJAX request received!")  
            # Respond with JSON for AJAX requests
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart.',
                'cart_count': cart.items.count()
            })
        else:
            return redirect(next_url)  # Redirect to the referring page
    else:
        # Handle session-based cart for non-authenticated users
        cart = request.session.get('cart', {})
        if str(product_id) not in cart:
            cart[str(product_id)] = {'quantity': 1, 'price': str(product.price)}
        else:
            cart[str(product_id)]['quantity'] += 1
        request.session['cart'] = cart  # Update the session

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Respond with JSON for AJAX requests
            return JsonResponse({
                'success': True,
                'message': 'Product added to cart.',
                'cart_count': len(request.session['cart'])
            })
        else:
            return redirect(next_url)  # Redirect to the referring page


def view_cart(request):
    if request.user.is_authenticated:
        # Handle authenticated users
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        # Add total_price to each item in the cart
        items_with_total = [
            {
                'product': item.product,
                'quantity': item.quantity,
                'total_price': float(item.product.price) * item.quantity  # Calculate total price for each CartItem
            }
            for item in items
        ]
        # Calculate subtotal using CartItem objects
        subtotal = sum(item['total_price'] for item in items_with_total)
    else:
        # Handle anonymous users with session-based cart
        cart = request.session.get('cart', {})
        items_with_total = [
            {
                'product': get_object_or_404(Product, id=prod_id),
                'quantity': details['quantity'],
                'price': details['price'],
                'total_price': float(details['price']) * details['quantity'],  # Calculate total price for each item
            }
            for prod_id, details in cart.items()
        ]
        # Calculate subtotal for session-based cart
        subtotal = sum(item['total_price'] for item in items_with_total)
    
    # Define shipping cost
    shipping_cost = 50
    # Calculate total
    total = subtotal + shipping_cost

    context = {
        'items': items_with_total,  # Pass the modified list with total_price
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'cart.html', context)



def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        # Handle authenticated users
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=item_id)
        cart_item.delete()

        # Send back updated cart count for authenticated users
        cart_count = cart.items.count()

        # Calculate updated subtotal and total
        items_data = [{
            'product_id': item.product.id,
            'total_price': item.quantity * item.product.price
        } for item in cart.items.all()]
        subtotal = sum(item['total_price'] for item in items_data)
        shipping = 50  # Shipping cost
        total = subtotal + shipping

    else:
        # Handle non-authenticated users (session-based cart)
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart  # Update the session

        # Send back updated cart count for non-authenticated users
        cart_count = len(request.session.get('cart', {}))

        # Calculate updated subtotal and total
        items_data = []
        subtotal = 0
        for pid, data in cart.items():
            try:
                product = Product.objects.get(id=pid)
                total_price = product.price * data['quantity']
                subtotal += total_price
                items_data.append({'product_id': pid, 'total_price': total_price})
            except Product.DoesNotExist:
                continue
        shipping = 50  # Shipping cost
        total = subtotal + shipping

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart.',
        'cart_count': cart_count,
        'items': items_data,
        'subtotal': subtotal,
        'total': total,
    })


def update_cart(request):
    if request.method == 'POST':
        updated_count = 0
        message = "Cart updated successfully."

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            for item_id, quantity in request.POST.items():
                if item_id.startswith('quantity_'):
                    try:
                        product_id = item_id.split('_')[1]
                        quantity = int(quantity)
                        product = get_object_or_404(Product, id=product_id)

                        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                        if cart_item:
                            if quantity <= 0:
                                cart_item.delete()
                            else:
                                cart_item.quantity = quantity
                                cart_item.save()
                    except (ValueError, IndexError):
                        continue

            updated_count = cart.items.count()
            items_data = [{
                'product_id': item.product.id,
                'total_price': item.quantity * item.product.price
            } for item in cart.items.all()]
            subtotal = sum(item['total_price'] for item in items_data)
            shipping = 50
            total = subtotal + shipping

        else:
            session_cart = request.session.get('cart', {})
            for item_id, quantity in request.POST.items():
                if item_id.startswith('quantity_'):
                    try:
                        product_id = item_id.split('_')[1]
                        quantity = int(quantity)
                        if product_id in session_cart:
                            if quantity <= 0:
                                del session_cart[product_id]
                            else:
                                session_cart[product_id]['quantity'] = quantity
                    except (ValueError, IndexError):
                        continue
            request.session['cart'] = session_cart
            updated_count = len(session_cart)

            items_data = []
            subtotal = 0
            for pid, data in session_cart.items():
                try:
                    product = Product.objects.get(id=pid)
                    total_price = product.price * data['quantity']
                    subtotal += total_price
                    items_data.append({'product_id': pid, 'total_price': total_price})
                except Product.DoesNotExist:
                    continue
            shipping = 50
            total = subtotal + shipping

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_count': updated_count,
                'items': items_data,
                'subtotal': subtotal,
                'total': total,
            })

        return redirect('cart')
    else:
        return HttpResponse(status=405)




def checkout(request):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Respond with JSON for AJAX requests when user is not authenticated
            return JsonResponse({
                'success': False,
                'message': 'Please log in first to proceed the checkout.',
                'redirect_url': '/login/'  # Provide the login URL for redirection
            })
        else:
            # If not an AJAX request, redirect to login
            return redirect('login')

    # Handle authenticated users
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    subtotal = sum(float(item.product.price) * item.quantity for item in items)
    
    shipping_cost = 45
    total = subtotal + shipping_cost

    context = {
        'items': items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }

    return render(request, 'checkout.html', context)

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML
from io import BytesIO

@login_required
def place_order(request):
    if request.method == 'POST':
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return redirect('cart')

        # Get form data
        billing_address = request.POST.get('billing_address')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        note = request.POST.get('note', '')
        payment_method = request.POST.get('payment_method')

        # Create Order
        order = Order.objects.create(
            user=user,
            billing_address=billing_address,
            name=name,
            email=email,
            phone=phone,
            note=note,
            total_price=cart.get_total_price(),
            payment_method=payment_method
        )

        cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                price=cart_item.product.price,
                quantity=cart_item.quantity,
            )

        # Delete cart
        cart_items.delete()
        cart.delete()

        # Prepare context for templates
        order_items = order.items.all()
        context = {
            'name': name,
            'order': order,
            'order_items': order_items,
            'billing_address': billing_address,
            'note': note,
            'request': request,  # Needed for PDF to resolve media/static
        }

        # ✅ Render HTML Email Body
        email_html = render_to_string('emails/order_confirmation.html', context)

        # ✅ Render PDF from clean invoice template
        pdf_html = render_to_string('emails/order_invoice.html', context)

        # ✅ Create PDF file
        pdf_file = BytesIO()
        HTML(string=pdf_html, base_url=request.build_absolute_uri()).write_pdf(pdf_file)

        # ✅ Send email
        subject = f"Order Confirmation - #{order.id}"
        email_msg = EmailMessage(
            subject=subject,
            body=email_html,
            from_email='furni@gmail.com',
            to=[email],
        )
        email_msg.content_subtype = 'html'
        email_msg.attach(f"invoice_{order.id}.pdf", pdf_file.getvalue(), 'application/pdf')
        email_msg.send()


        # Redirect
        if payment_method == 'Online Payment':
            return redirect('payment')
        else:
            return redirect('payment_cod')

    return redirect('checkout')


# def payment(request):
#     return render(request, 'payment.html')

@login_required
def payment(request):
    user = request.user
    order = Order.objects.filter(user=user).order_by('-created_at').first()

    if order:
        total = order.total_price
    else:
        total = 0

    return render(request, 'payment.html', {'total': total})

# def payment_success(request):
#     return render(request, 'payment_success.html')

@login_required
def payment_cod(request):
    user = request.user
    order = Order.objects.filter(user=user).order_by('-created_at').first()

    if order:
        total = order.total_price
    else:
        total = 0

    return render(request, 'payment_success_cod.html', {
        'total': total,
        'order' : order
        })

@login_required
def payment_success(request):
    user = request.user
    order = Order.objects.filter(user=user).order_by('-created_at').first()

    if order:
        total = order.total_price
    else:
        total = 0

    return render(request, 'payment_success.html', {
        'total': total,
        'order' : order
        })

def user_orders(request):
    if request.user.is_authenticated:
        # Handle authenticated users
        cart, created = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        # Calculate subtotal using CartItem objects
        subtotal = sum(float(item.product.price) * item.quantity for item in items)
    else:
        # Handle anonymous users with session-based cart
        cart = request.session.get('cart', {})
        items = [
            {
                'product': get_object_or_404(Product, id=prod_id),
                'quantity': details['quantity'],
                'price': details['price'],
            }
            for prod_id, details in cart.items()
        ]
        subtotal = sum(float(item['price']) * item['quantity'] for item in items)

    # Define shipping cost
    shipping_cost = 45
    # Calculate total
    total = subtotal + shipping_cost

    context = {
        'items': items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    }
    
    return render(request, 'orders.html', context)


# if you want to keep items when user added to cart as a login user with non login user 



@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    # Check if the session has a cart
    session_cart = request.session.get('cart', None)

    if session_cart:
        # Get or create the cart for the logged-in user
        cart, created = Cart.objects.get_or_create(user=user)

        for prod_id, details in session_cart.items():
            product = get_object_or_404(Product, id=prod_id)

            # Check if the product is already in the user's cart
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if not created:
                # If product already exists, increase the quantity
                cart_item.quantity += details['quantity']
            else:
                # If product doesn't exist, add it to the cart
                cart_item.quantity = details['quantity']

            cart_item.save()

        # Clear the session cart after merging
        del request.session['cart']


@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'order_detail.html', {'order': order, 'items': items})
