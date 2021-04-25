from typing import List
from .comments import Comment
from flask import url_for

HTML_COMMENTS = '''<div class="mar-btm">
 <a href="/users/{user_id}" style="font-size: 16pt;" class="btn-link text-semibold media-heading box-inline">{username}</a>
 <p class="text-muted text-sm"><i class="fa fa-mobile fa-lg"></i>{date}</p>
 </div>
 <p style="font-size: 14pt;">{text}</p>
 <div class="pad-ver">
 <a class="btn btn-sm btn-default btn-hover-primary btn-outline-info" href="{url}">Ответить</a>
 </div>
 <hr>'''

HTML_FORM = '''   <form action="" method="post" class="form-inline pb-2" style="padding-left: 5px;">
        {{ form.hidden_tag() }}
        <p>
            {{ form.content(class="form-control") }}
            {% for error in form.content.errors %}
                <p class="alert alert-danger" role="alert">
                    {{ error }}
                </p>
            {% endfor %}
        </p>
        <p>{{ form.submit_second(type="submit", class="btn btn-primary m-2") }}</p>
</form>'''


def reformat_comments(comments: List[Comment], to_id=None, reply_id=None):
    html_code = ''
    need_comments = [c for c in comments if c.to_id == to_id]
    if not need_comments:
        return ''

    for comment in need_comments:
        text_1 = HTML_COMMENTS.format(username=comment.user.name,
                                      date=comment.created_date.strftime(
                                          '%e %b %Y'),
                                      text=comment.text,
                                      url=url_for('show_post',
                                                  post_id=comment.post_id,
                                                  reply_to=comment.id), user_id=comment.user_id)
        text_2 = '''<div class="media-block">
                        <a class="media-left" href="/users/{user_id}">
                            <img class="img-circle img-sm" 
                            alt="Профиль пользователя" src="{url}" style="border-radius: 50%;
                            margin-right: 20px;">
                        </a>
                    <div class="media-body">'''.format(
            url=url_for('static', filename='img/users/') + comment.user.icon,
            user_id=comment.user_id)
        html_code += text_2 + text_1 + reformat_comments(comments, comment.id,
                                                         reply_id)

        if reply_id == str(comment.id):
            html_code += HTML_FORM

        html_code += '''</div></div>'''

    return html_code
