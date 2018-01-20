#!/usr/bin/python
# -*- coding: utf-8 -*-

import utils

# email_info = {
#     'class_name': class_name_i,
#     'teacher_fullname': teacher_fullname_i,
#     'week_start': week_start_ymd,
#     'week_end': week_end_ymd,
#     'stat': stat,
#     'best_group_comp': best_group_comp,
#     'worst_group_comp': worst_group_comp,
#     'best_indiv_comp': best_indiv_comp,
#     'worst_indiv_comp': worst_indiv_comp,
# }


# e.g. translate (1, 2, 3) to "1, 2, 3"
# param: tu
def tuple2str(tu, sep):
    tu_list = []
    for item in tu:
        tu_list.append(str(item))

    return sep.join(tu_list)


# "This is emample" -> "<tag>This is example</tag>""
def add_html_tag(tag, content):
    return "<{}>".format(tag) + content + "</{}>".format(tag)

def add_hylink(link, content):
    return "<a href='{}'>".format(link) + content + "</a>"

# e.g. <p style="padding-left:3em;margin:2px;" name="para">This is Para</p>
# @ **prpty : a dict contains all key value paris
# e.g. prpty = {
#          "style": "padding-left:3em;margin:2px;",
#          "name": "para"
#        }
def add_html_tag_with_prpty(tag, content, **prpty):

    prpty_list = []

    for (k, v) in prpty.items():
        item = '{}="{}"'.format(k, v)
        prpty_list.append(item)

    prpty_str = " ".join(prpty_list)
    prefix = "<{} {}>".format(tag, prpty_str)
    suffix = "</{}>".format(tag)

    return prefix + content + suffix



def get_stat(is_null, group_rev_count):
    if is_null:
        stat = "Not a single group made any revisions this week. Please consider encouraging students to contribute more actively.</p>"
    else:
        avg = utils.mean(group_rev_count)
        sd = utils.stdev(group_rev_count)
        stat = "In this class, the average number of revisions per group is {}. Following is a brief analysis of weekly performance of the class.<p>".format(
        avg)
        print(sum(group_rev_count), avg, sd)

    return stat


def get_best_group_comp(len_best_group, best_group_no, best_group_rev_count):
    '''
    Below is an e.g.
    ==================

    Group comparsion  #(title)
    Top 3 groups with the most revisions: #(sub_title)

    1. Group 2 (85 revisions) #(content)
    2. Group 4 (33 revisions)
    3. Group 8 (17 revisions)
    '''

    if len_best_group < 1:
        return ""

    if len_best_group == 1:
        sub_title = "The only group made revision:"
    else:
        sub_title = "Top {} groups with the most revisions:".format(len_best_group)


    title = "Group comparsion"
    title = add_html_tag('b', title)
    title = add_html_tag('u', title)
    title += "<br>"


    content_list = []

    for i in range(0, len_best_group):
        record = "{}. Group {} ({} revisions)".format(i + 1, best_group_no[i], best_group_rev_count[i])
        content_list.append(record)

    content = "<br>".join(content_list)


    prpty = {
        "style" : "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = title + sub_title + content

    return text


def gen_email_text(addr_from, addr_to, subj, *bcc, **info):
    bcc_str = tuple2str(bcc, ", ")
    subj_str = "{} - {}".format(subj, info['class_name'])

    headers = """\
From: {0}
To: {1}
Bcc: {2}
Content-Type: text/html
Subject: {3}


	""".format(addr_from, addr_to, bcc_str, subj_str)

    html_title = add_html_tag('title', subj)
    html_title = add_html_tag('head', html_title)

    html_body = """\
	Dear {0} <p><br>
	This is a weekly summary ({1} - {2}) of students' performance in Class {3}.

	""".format(info['teacher_fullname'], info['week_start'], info['week_end'], info['class_name'][-2:])

    html_body += info['stat']
    html_body += info['best_group_comp']
    html_body += info['worst_group_comp']
    html_body += info['best_indiv_comp']
    html_body += info['worst_indiv_comp']

    # conclusion = "Please log in to <a href='http://ccmir.cite.hku.hk/wikiglass/'>Wikiglass Site</a> for more details at any time. Data on Wikiglass are updated everyday.<p><br>" \
    # + "Yours sincerely,<br>Wikiglass</body></html>\n\n"

    conclusion = "Please log into {} from more details at any time. Data on Wikiglass are updated everyday.<p><br>Yours sincerely,<br>Wikiglass"\
        .format('http://ccmir.cite.hku.hk/wikiglass/', 'Wikiglass Site')

    html_body += conclusion

    html_body = add_html_tag('body', html_body)

    content = html_title + html_body

    content = add_html_tag('html', content)

    text = headers + content
    return text
















if __name__ == '__main__':
    addr_from = 'wikiglass@ccmir.cite.hku.hk'
    addr_to = 'josephchuh7@gmail.com'
    # bcc = ('123@qq.com', '456@gmail.com', '789@hku.hk')
    bcc = ()
    subj = 'Weekly Summary'

    text = gen_email_text(addr_from, addr_to, subj, *bcc, **info)
    print text