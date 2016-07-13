from threading import Thread
from flask import current_app, render_template
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content


def send_async_email(app, sg, mail):
    with app.app_context():
        response = sg.client.mail.send.post(request_body=mail.get())


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])

    from_email = Email(app.config['MAIL_SENDER'])
    subject = app.config['MAIL_PREFIX'] + ' ' + subject
    to_email = Email(to)
    content = Content("text/plain", render_template(template + '.txt', **
                                                    kwargs))
    mail = Mail(from_email, subject, to_email, content)

    #msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, sg, mail])
    thr.start()
    return thr
