from app.models import Feed
from email.mime.text import MIMEText
from flask import request
from jinja2 import FileSystemLoader
from jinja2 import Environment
import asyncio
import smtplib
import os

env = Environment(
    loader=FileSystemLoader('{}/templates'.format(os.path.dirname(__file__)))
)
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login(os.getenv('MAIL_ID'), os.getenv('MAIL_PW'))


def render_template(template, **kwargs):
    template = env.get_template(template)

    return template.render(kwargs)


async def send_mail(feed, reason):
    from_email = 'semicolondsm@gmail.com'
    to_email = 'semicolondsm@gmail.com'
    subject = '피드 신고 피드백'

    template = render_template('report.html', feed=feed, reason=reason)
    message = MIMEText(template, 'html')
    message['Subject'] = subject
    message['From'] = from_email
    message['To'] = to_email

    smtp.sendmail(from_email, to_email, message.as_string())


# 신고 API
def report():
    json = request.json
    feed = Feed.query.get(json.get('feed_id'))
    reason = json.get('reason')
    asyncio.run(send_mail(feed=feed, reason=reason))
    return {'msg': '신고가 성공적으로 작성되었습니다.'}, 201