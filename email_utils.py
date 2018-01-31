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



def get_stat(group_rev_count):

    if len(group_rev_count) == 0:
        stat = "Not a single group made any revisions this week. Please consider encouraging students to contribute more actively.</p>"
    else:
        avg = utils.mean(group_rev_count)
        sd = utils.stdev(group_rev_count)
        stat = "In this class, the average number of revisions per group is {}. Following is a brief analysis of weekly performance of the class.<p>".format(
        avg)
        print(sum(group_rev_count), avg, sd)

    return stat

def get_stat_grade(cls_avg_list):

    #title = "The average number of revisions per group"
    title = "Average revisions"

    title = add_html_tag('b', title)
    title = add_html_tag('u', title)
    title += "<br>"


    sub_title = "The average number of revisions per group is as follows:"

    content = ""

    for row in cls_avg_list:
        content += "{} : {} revisions<br>".format(row[0], row[1])

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)


    following =  "Following is a brief analysis of weekly performance of all classes."
    following = add_html_tag('p', following)

    text = title + sub_title + content + following
    return text


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

def get_best_group_comp_grade(best_group_list):
    '''
        Below is an e.g.
        ==================

        Group comparsion  #(title)
        Top 3 groups with the most revisions: #(sub_title)

        1. Group 2 (85 revisions) #(content)
        2. Group 4 (33 revisions)
        3. Group 8 (17 revisions)
        '''

    len_best_group = len(best_group_list)

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

    for i in range(len_best_group):
        record = "{}. {} ({} revisions)".format(i + 1, best_group_list[i][0], best_group_list[i][1])
        content_list.append(record)

    content = "<br>".join(content_list)

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = title + sub_title + content

    return text

def get_worst_group_comp(no_of_groups, worst_group_no, worst_group_rev_count, zero_list):
    text = ""

    sub_title = "3 groups with the fewest revisions:"

    content_list = []

    len_zero = len(zero_list)

    if len_zero == 0:
        for i in range(0, 3):
            record = "{}. Group {} ({} revisions)".format(i + 1, worst_group_no[i], worst_group_rev_count[i])
            content_list.append(record)

    elif len_zero < 3:

        index = 1
        for i in range(0, len_zero):
            record = "{}. Group {} ({} revisions)".format(index, zero_list[i][0], 0)
            content_list.append(record)
            index += 1

        for i in range(0, 3 - len_zero):
            record = "{}. Group {} ({} revisions)".format(index, worst_group_no[i], worst_group_rev_count[i])
            content_list.append(record)
            index += 1

    elif len_zero == no_of_groups:
        return text
    else:
        sub_title = "Groups without making any revisions:"

        for i in range(0, len_zero):
            record = "{}. Group {}".format(i + 1, zero_list[i][0])
            content_list.append(record)

    content = "<br>".join(content_list)

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = sub_title + content

    return text

def get_worst_group_comp_grade(worst_group_list, zero_goup_list):

    text = ""
    content_list = []

    if len(zero_goup_list) > len(worst_group_list):# show all zero group
        sub_title = "Groups without making any revisions:"

        for i in range(len(zero_goup_list)):
            record = "{}. {}".format(i + 1, zero_goup_list[i])
            content_list.append(record)

    else:
        sub_title = "3 groups with the fewest revisions:"

        for i in range(len(worst_group_list)):
            record = "{}. {} ({} revisions)".format(i + 1, worst_group_list[i][0], worst_group_list[i][1])
            content_list.append(record)

    content = "<br>".join(content_list)

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = sub_title + content

    return text

def get_best_stu_info(best_stu_list):
    '''
    best_stu_info = {
        "best_stu_name" : best_stu_name,
        "best_stu_add" : best_stu_add,
        "best_stu_del" : best_stu_del
    }
    '''

    best_stu_name = []
    best_stu_add = []
    best_stu_del = []

    for row in best_stu_list:
        user_name = row[1].encode('utf-8')
        total_a = row[5]
        total_d = row[6]
        best_stu_name.append(user_name)
        best_stu_add.append(total_a)
        best_stu_del.append(total_d)

    return {
        "best_stu_name": best_stu_name,
        "best_stu_add": best_stu_add,
        "best_stu_del": best_stu_del
    }

# NOTE: Please follow the format of best_stu_info given in comment when calling this function
def get_best_indiv_comp(**best_stu_info):

    '''
    best_stu_info = {
        "best_stu_name" : best_stu_name,
        "best_stu_add" : best_stu_add,
        "best_stu_del" : best_stu_del
    }

    '''
    if not best_stu_info:
        return ""

    best_stu_name = best_stu_info["best_stu_name"]
    best_stu_add = best_stu_info["best_stu_add"]
    best_stu_del = best_stu_info["best_stu_del"]

    title = "Individual performance"
    title = add_html_tag('b', title)
    title = add_html_tag('u', title)
    title += "<br>"

    len_best = len(best_stu_name)

    if len_best >= 2:
        sub_title = "Top {} students with the most contributions:".format(len_best)
    else : #len_best == 1
        sub_title = "The top student with the most contribution is:"

    content_list = []

    for i in range (0, len_best):
        record = "{0}. {1} ({2} words added, {3} words deleted)".format(i + 1, best_stu_name[i], best_stu_add[i], best_stu_del[i])
        content_list.append(record)

    content = "<br>".join(content_list)

    prpty = {
        "style" : "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = title + sub_title + content

    return text

def get_best_indiv_comp_grade(**best_stu_info):

    '''
    best_stu_info = {
        "best_stu_class" : best_stu_class,
        "best_stu_name" : best_stu_name,
        "best_stu_add" : best_stu_add,
        "best_stu_del" : best_stu_del
    }

    '''
    if not best_stu_info:
        return ""

    best_stu_class = best_stu_info["best_stu_class"]
    best_stu_name = best_stu_info["best_stu_name"]
    best_stu_add = best_stu_info["best_stu_add"]
    best_stu_del = best_stu_info["best_stu_del"]

    title = "Individual performance"
    title = add_html_tag('b', title)
    title = add_html_tag('u', title)
    title += "<br>"

    len_best = len(best_stu_name)

    if len_best >= 2:
        sub_title = "Top {} students with the most contributions:".format(len_best)
    else : #len_best == 1
        sub_title = "The top student with the most contribution is:"

    content_list = []

    for i in range (0, len_best):
        record = "{0}. {1} {2} ({3} words added, {4} words deleted)".format(i + 1, best_stu_class[i], best_stu_name[i], best_stu_add[i], best_stu_del[i])
        content_list.append(record)

    content = "<br>".join(content_list)

    prpty = {
        "style" : "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)

    text = title + sub_title + content

    return text

def get_worst_stu_info(worst_stu_list):
    '''

    worst_stu_info = {
    "worst_stu_name" : worst_stu_name,  # @worst_stu_name should only contains names of those whose revision number > 0
    "worst_stu_add" : worst_stu_add,    # so is @worst_stu_add
    "worst_stu_del" : worst_stu_del.    # and @worst_stu_del
}
    '''

    worst_stu_name = []
    worst_stu_add = []
    worst_stu_del = []

    for row in worst_stu_list:
        if row[7] != 0:
            worst_stu_name.append(row[1].encode('utf-8'))
            worst_stu_add.append(row[5])
            worst_stu_del.append(row[6])

    return {
        "worst_stu_name": worst_stu_name,
        "worst_stu_add" : worst_stu_add,
        "worst_stu_del" : worst_stu_del
    }

# NOTE: Please follow the format of worst_stu_info given in comment when calling this function
def get_worst_indiv_comp(zero_stu_list=(), **worst_stu_info):

    '''
    worst_stu_info = {
        "worst_stu_name" : worst_stu_name,  # @worst_stu_name should only contains names of those whose revision number > 0
        "worst_stu_add" : worst_stu_add,    # so is @worst_stu_add
        "worst_stu_del" : worst_stu_del.    # and @worst_stu_del
    }

    '''

    if not zero_stu_list and not worst_stu_info:
        return ""

    worst_stu_name = worst_stu_info['worst_stu_name']
    worst_stu_add = worst_stu_info['worst_stu_add']
    worst_stu_del = worst_stu_info['worst_stu_del']

    len_worst = len(worst_stu_name)
    len_zero = len(zero_stu_list)

    content_list = []

    if len_worst == 0 or len_zero >= 5:  # all students have 0 revisions

        sub_title = "Students without making any revisions:"

        for i in range(0, len_zero):
            record = "{}. {}".format(i + 1, zero_stu_list[i])
            content_list.append(record)

    else:  # as long as len_worst >0 and len_zero <5, len_worst + len_zero == 5
        sub_title = "5 students with the fewest contributions:"

        index = 1

        for i in range(0, len_zero):
            record = "{}. {} (0 words added, 0 words deleted)".format(index, zero_stu_list[i])
            content_list.append(record)
            index += 1

        for i in range(0, len_worst):
            record = "{}. {} ({} words added, {} words deleted)".format(index, worst_stu_name[i], worst_stu_add[i],
                                                                        worst_stu_del[i])
            content_list.append(record)
            index += 1

    content = "<br>".join(content_list)

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)
    content += "<br>"

    text = sub_title + content

    return text


# NOTE: Please follow the format of worst_stu_info given in comment when calling this function
def get_worst_indiv_comp_grade(zero_stu_list=(), **worst_stu_info):

    '''
    worst_stu_info = {
        "worst_stu_class" : worst_stu_class,
        "worst_stu_name" : worst_stu_name,  # @worst_stu_name should only contains names of those whose revision number > 0
        "worst_stu_add" : worst_stu_add,    # so is @worst_stu_add
        "worst_stu_del" : worst_stu_del.    # and @worst_stu_del
    }

    '''

    if not zero_stu_list and not worst_stu_info:
        return ""

    worst_stu_class = worst_stu_info["worst_stu_class"]
    worst_stu_name = worst_stu_info['worst_stu_name']
    worst_stu_add = worst_stu_info['worst_stu_add']
    worst_stu_del = worst_stu_info['worst_stu_del']

    len_worst = len(worst_stu_name)
    len_zero = len(zero_stu_list)

    content_list = []

    if len_worst == 0 or len_zero >= 5:  # all students have 0 revisions

        sub_title = "Students without making any revisions:"

        for i in range(0, len_zero):
            record = "{}. {} {}".format(i + 1, zero_stu_list[i][0], zero_stu_list[i][1])
            content_list.append(record)

    else:  # as long as len_worst >0 and len_zero <5, len_worst + len_zero == 5
        sub_title = "5 students with the fewest contributions:"

        index = 1

        for i in range(0, len_zero):
            record = "{}. {} {} (0 words added, 0 words deleted)".format(index, zero_stu_list[i][0], zero_stu_list[i][1])
            content_list.append(record)
            index += 1

        for i in range(0, len_worst):
            record = "{0}. {1} {2} ({3} words added, {4} words deleted)".format(index, worst_stu_class[i], worst_stu_name[i], worst_stu_add[i],
                                                                        worst_stu_del[i])
            content_list.append(record)
            index += 1

    content = "<br>".join(content_list)

    prpty = {
        "style": "padding-left:3em;margin:2px;"
    }

    content = add_html_tag_with_prpty('p', content, **prpty)
    content += "<br>"

    text = sub_title + content

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

def gen_email_text_grade(addr_from, addr_to, subj, *bcc, **info):
    bcc_str = tuple2str(bcc, ", ")
    subj_str = "{} - {}".format(subj, info['grade'])

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
    	This is a weekly summary ({1} - {2}) of students' performance in ALL classes of {3}.</p>

    	""".format(info['teacher_fullname'], info['week_start'], info['week_end'], info['grade'])

    html_body += info['stat']
    html_body += info['best_group_comp']
    html_body += info['worst_group_comp']
    html_body += info['best_indiv_comp']
    html_body += info['worst_indiv_comp']

    # conclusion = "Please log in to <a href='http://ccmir.cite.hku.hk/wikiglass/'>Wikiglass Site</a> for more details at any time. Data on Wikiglass are updated everyday.<p><br>" \
    # + "Yours sincerely,<br>Wikiglass</body></html>\n\n"

    conclusion = "Please log into {} from more details at any time. Data on Wikiglass are updated everyday.<p><br>Yours sincerely,<br>Wikiglass" \
        .format('http://ccmir.cite.hku.hk/wikiglass/', 'Wikiglass Site')

    html_body += conclusion

    html_body = add_html_tag('body', html_body)

    content = html_title + html_body

    content = add_html_tag('html', content)

    text = headers + content
    return text


if __name__ == '__main__':
    # addr_from = 'wikiglass@ccmir.cite.hku.hk'
    # addr_to = 'josephchuh7@gmail.com'
    # # bcc = ('123@qq.com', '456@gmail.com', '789@hku.hk')
    # bcc = ()
    # subj = 'Weekly Summary'
    #
    # text = gen_email_text(addr_from, addr_to, subj, *bcc, **info)
    # print text
    pass