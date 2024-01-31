from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.shortcuts import render
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created, payment_completed
from cart.cart import Cart
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.template.loader import render_to_string

from django.http import HttpResponse
from django.template.loader import render_to_string

from django.shortcuts import get_object_or_404
from orders.models import Order
from django.contrib.admin.views.decorators import staff_member_required
from xhtml2pdf import pisa

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    data = {'order': order}
    pdf_html = render_to_string('orders/order/pdf.html', data)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    pisa_status = pisa.CreatePDF(
        render_to_string('orders/order/pdf.html', data), dest=response
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            # clear the cart
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # задать заказ в сеансе
            request.session['order_id'] = order.id

            return render(request,
                          'orders/order/created.html',
                          {'order': order})
            # или, если интегрирована система платежей
            # перенаправить к платежу
            #return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})
