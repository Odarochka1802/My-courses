
from django.core.mail import send_mail
from io import BytesIO
from celery import shared_task
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order

@shared_task
def order_created(order_id):
    """
    Task to send an e-mail notification when an order is
    successfully created.
    """
    order = Order.objects.get(id=order_id)
    subject = f'Order nr. {order.id}'
    message = f'Dear {order.first_name},\n\n' \
              f'You have successfully placed an order.' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject,
                          message,
                          'admin@myshop.com',
                          [order.email])
    return mail_sent



@shared_task
def payment_completed(order_id):
    """
    Задание по отправке уведомления по электронной почте
    при успешной оплате заказа.
    """
    order = Order.objects.get(id=order_id)
    # создаем письмо с счётом
    subject = f'My Shop – Счёт № {order.id}'
    message = 'Пожалуйста, прикреплён счёт за вашу недавнюю покупку.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])
    # генерируем PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    # Генерируем PDF с помощью pisa
    pdf = pisa.CreatePDF(html, dest=out, link_callback=settings.MEDIA_URL)
    if not pdf.err:
        # прикрепляем PDF к письму
        email.attach(f'order_{order.id}.pdf', out.getvalue(), 'application/pdf')
        # отправляем письмо
        email.send()
