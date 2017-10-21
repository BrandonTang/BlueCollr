from app import mail

from flask import current_app, render_template
from flask_mail import Message
from threading import Thread


def send_email(to, subject, template, **kwargs):
    """
    Sends an e-mail.
    :param to: The recipient
    :param subject: E-mail subject field
    :param template: E-mail template
    :param kwargs: Any additional arguments
    :return: A thread to be used in send_async_email
    """
    app = current_app._get_current_object()
    msg = Message('BlueCollr' + ' ' + subject, sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr