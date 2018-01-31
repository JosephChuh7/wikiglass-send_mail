#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import plag_summary
import utils
import db_utils
import email_utils

# assign zero to groups that made 0 revisions
# parameters:
# @rev_grp_list: a list of group numbers that have revisions
# @all_grp_list: a list of all group numbers
# @group_rev_cnt_list: a 2D list of group that have revisions, contains two fields: group_no, count like [[1, 34], [2, 45] ...]
# return : @group_rev_cnt_list in utf-8
def assign_zero(all_grp_list, group_rev_cnt_list):

    if not len(group_rev_cnt_list) < len(all_grp_list):
        return group_rev_cnt_list

    all_grp_list = utils.list_2d_encode_utf8(all_grp_list)
    group_rev_cnt_list = utils.list_2d_encode_utf8(group_rev_cnt_list)

    rev_grp_list = []

    for row in group_rev_cnt_list:
        rev_grp_list.append(row[0])

    for group_number in all_grp_list:
        if group_number[0] not in rev_grp_list:
            temp = [group_number[0], 0]
            group_rev_cnt_list.append(temp)

    return group_rev_cnt_list

def get_grp_rev_avg(group_rev_cnt_list):
    group_rev_cnt = []
    for row in group_rev_cnt_list:
        group_rev_cnt.append(row[1])

    return utils.mean(group_rev_cnt)

def get_worst_group_comp(group_rev_cnt_list, no_of_groups, num):
    len_group_rev_cnt_list = len(group_rev_cnt_list)

    if len_group_rev_cnt_list < num:
        num = len_group_rev_cnt_list

    worst_group = []

    # Get a list of the worst 3 groups
    for i in range(0, num):
        if group_rev_cnt_list[i][1] != 0:
            worst_group.append(group_rev_cnt_list[i])

    worst_group_no = []
    worst_group_rev_count = []

    zero_groups = []  # all groups with zero revision counts
    for row in worst_group:
        worst_group_no.append(row[0])
        worst_group_rev_count.append(row[1])

    for row in group_rev_cnt_list:
        if row[1] == 0:
            zero_groups.append(row)

    return email_utils.get_worst_group_comp(no_of_groups, worst_group_no, worst_group_rev_count, zero_groups)

def get_best_stu_info(best_stu_list):
    '''
    best_stu_info = {
        "best_stu_name" : best_stu_name,
        "best_stu_add" : best_stu_add,
        "best_stu_del" : best_stu_del
    }
    '''

    best_stu_class = []
    best_stu_name = []
    best_stu_add = []
    best_stu_del = []

    for row in best_stu_list:
        user_id = row[2].encode("utf-8")
        stu_class_id = user_id[:2]
        user_name = row[1].encode('utf-8')
        total_a = row[5]
        total_d = row[6]
        best_stu_class.append(stu_class_id)
        best_stu_name.append(user_name)
        best_stu_add.append(total_a)
        best_stu_del.append(total_d)

    return {
        "best_stu_class": best_stu_class,
        "best_stu_name": best_stu_name,
        "best_stu_add": best_stu_add,
        "best_stu_del": best_stu_del
    }

# @num : the number of students to show
# e.g. for "Top 3 students", num should be 3
def get_best_indiv_comp(best_stu_list):

    best_stu_info = get_best_stu_info(best_stu_list)
    return email_utils.get_best_indiv_comp_grade(**best_stu_info)

def get_worst_stu_info(worst_stu_list):
    '''
    worst_stu_info = {

    "worst_stu_name" : worst_stu_name,  # @worst_stu_name should only contains names of those whose revision number > 0
    "worst_stu_add" : worst_stu_add,    # so is @worst_stu_add
    "worst_stu_del" : worst_stu_del.    # and @worst_stu_del
}
    '''

    worst_stu_class = []
    worst_stu_name = []
    worst_stu_add = []
    worst_stu_del = []

    for row in worst_stu_list:
        if row[7] != 0:
            stu_class_id = row[2].encode("utf-8")
            worst_stu_class.append(stu_class_id[:2])
            worst_stu_name.append(row[1].encode('utf-8'))
            worst_stu_add.append(row[5])
            worst_stu_del.append(row[6])

    return {
        "worst_stu_class" : worst_stu_class,
        "worst_stu_name": worst_stu_name,
        "worst_stu_add": worst_stu_add,
        "worst_stu_del": worst_stu_del
    }

def get_worst_indiv_comp(worst_stu_list, zero_stu_list_utf8):

    worst_stu_info = get_worst_stu_info(worst_stu_list)

    zero_stu_list = []

    for row in zero_stu_list_utf8:
        stu_name = row[0].encode('utf-8')
        stu_no = row[1].encode('utf-8')
        stu_class_id = stu_no[:2]

        tu = (stu_class_id, stu_name)
        zero_stu_list.append(tu)


    return email_utils.get_worst_indiv_comp_grade(zero_stu_list, **worst_stu_info)

def get_stat(group_rev_cnt_list):
    group_rev_count = []

    for row in group_rev_cnt_list:
        group_rev_count.append(row[1])

    return email_utils.get_stat(group_rev_count)


def get_group_comp(conn, class_list, week_start, week_end, num2show):


    all_grp_list = []
    cls_avg_list = [] #class name and its avg rev num

    for class_id in class_list:

        class_id = class_id[0].encode("utf-8")
        # Get a list of revision counts of each group
        sql_get_rev_cnt_list = """  SELECT t.group_no, COUNT(t.group_no) AS count
                                                FROM (
                                                    SELECT Wiki.group_no AS group_no
                                                    FROM Revision, User, Page, Wiki
                                                    WHERE Revision.user_id = User.user_id
                                                    AND Revision.page_id = Page.Page_id
                                                    AND Page.wiki_id = Wiki.wiki_id
                                                    AND Wiki.class_name = '{0}'
                                                    AND perm = 'write'
                                                    AND Revision.timestamp BETWEEN '{1}' AND '{2}') t
                                                    GROUP BY group_no""".format(class_id, week_start, week_end)

        group_rev_cnt_list = db_utils.db_exec(conn, sql_get_rev_cnt_list)

        sql_get_grp_list = "SELECT group_no FROM Wiki WHERE class_name ='{}'".format(class_id)

        group_list = db_utils.db_exec(conn, sql_get_grp_list)

        #group_rev_cnt_list assign_zero
        group_rev_cnt_list = assign_zero(group_list, group_rev_cnt_list)

        cls_name = class_id[-2:]
        cls_name = cls_name.upper()

        tu = (cls_name, get_grp_rev_avg(group_rev_cnt_list))
        cls_avg_list.append(tu)

        for row in group_rev_cnt_list:
            cls_grp = "{} group {}".format(cls_name, row[0].encode("utf-8"))
            record = (cls_grp, row[1])
            all_grp_list.append(record)


    all_grp_list.sort(key=lambda x: x[1])

    num = num2show

    best_group_list = all_grp_list[(0 - num):] #last few items
    best_group_list = best_group_list[::-1] #reverse
    worst_group_list = all_grp_list[:num] #first few items

    zero_group_list = []
    for row in all_grp_list:
        if row[1] > 0:
            break
        else:
            zero_group_list.append(row[0])


    return {
        "cls_avg_list" : cls_avg_list,
        "best_group_list" : best_group_list,
        "worst_group_list" : worst_group_list,
        "zero_group_list" : zero_group_list
    }

def get_indiv_comp(conn, grade, week_start, week_end, num2show):
    # Get a list of the Best 5 students
    sql_get_best = """SELECT User_id, User_name, User_no, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change)
                                            FROM Revision_Stats, Page, Wiki
                                            WHERE Revision_Stats.page_id = Page.Page_id
                                            AND Page.wiki_id = Wiki.wiki_id
                                            AND Wiki.class_name like '{0}%'
                                            AND Revision_creation_time BETWEEN '{1}' AND '{2}'
                                            AND User_perm = 'write'
                                            GROUP BY User_id
                                            ORDER BY SUM(Words_change)DESC LIMIT {3}""".format(grade, week_start,
                                                                                             week_end, num2show)

    best_stu_list = db_utils.db_exec(conn, sql_get_best)

    # Get a list of the worst 5 students
    sql_get_worst = """SELECT User_id, User_name, User_no, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change)
                                                FROM Revision_Stats, Page, Wiki
                                                WHERE Revision_Stats.page_id = Page.Page_id
                                                AND Page.wiki_id = Wiki.wiki_id
                                                AND Wiki.class_name like '{0}%'
                                                AND Revision_creation_time BETWEEN '{1}' AND '{2}'
                                                AND User_perm = 'write'
                                                GROUP BY User_id
                                                ORDER BY SUM(Words_change)ASC LIMIT {3}""".format(grade, week_start,
                                                                                                week_end, num2show)
    worst_stu_list = db_utils.db_exec(conn, sql_get_worst)

    sql_get_zero = """SELECT t.stu_name, t.stu_num FROM (
                                          SELECT User_id, User_name as stu_name, User_no as stu_num, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change) AS s
                                                FROM Revision_Stats, Page, Wiki
                                                WHERE Revision_Stats.page_id = Page.Page_id
                                                AND Page.wiki_id = Wiki.wiki_id
                                                AND Wiki.class_name like '{}%'
                                                AND Revision_creation_time BETWEEN '{}' AND '{}'
                                                AND User_perm = 'write'
                                                GROUP BY User_id
                                                ORDER BY SUM(Words_change))t
                          WHERE t.s = 0
                                                """.format(grade, week_start, week_end)

    zero_stu_list_utf8 = db_utils.db_exec(conn, sql_get_zero)

    best_indiv_comp = get_best_indiv_comp(best_stu_list)
    worst_indiv_comp = get_worst_indiv_comp(worst_stu_list, zero_stu_list_utf8)

    return {
        "best_indiv_comp" : best_indiv_comp,
        "worst_indiv_comp" : worst_indiv_comp
    }

#@grade = '2017pkps5'
def get_email_text(conn, class_list, grade, week_start, week_end, teacher_email_i, teacher_fullname_i):

    #Group Performance
    group_comp = get_group_comp(conn, class_list, week_start, week_end, 5)

    best_group_list = group_comp["best_group_list"]
    worst_group_list = group_comp["worst_group_list"]
    zero_group_list = group_comp["zero_group_list"]
    cls_avg_list = group_comp["cls_avg_list"]

    best_group_comp = email_utils.get_best_group_comp_grade(best_group_list)
    worst_group_comp = email_utils.get_worst_group_comp_grade(worst_group_list, zero_group_list)

    stat = email_utils.get_stat_grade(cls_avg_list)

    #Individual Performance
    indiv_comp = get_indiv_comp(conn, grade, week_start, week_end, 10)

    best_indiv_comp = indiv_comp["best_indiv_comp"]
    worst_indiv_comp = indiv_comp["worst_indiv_comp"]



    #teacher_email_i = 'josephchuh7@gmail.com'
    teacher_email_i = 'xh.gslis@gmail.com'

    addr_from = 'wikiglass@ccmir.cite.hku.hk'
    addr_to = teacher_email_i
    subj = 'Weekly Summary'
    bcc = ('josephchuh7@gmail.com',)
    #bcc = ()

    email_info = {
        'teacher_fullname': teacher_fullname_i,
        'grade' : grade,
        'week_start': week_start_ymd,
        'week_end': week_end_ymd,
        'stat': stat,
        'best_group_comp': best_group_comp,
        'worst_group_comp': worst_group_comp,
        'best_indiv_comp': best_indiv_comp,
        'worst_indiv_comp': worst_indiv_comp,
    }

    # Bcc: ecswikis@gmail.com, xh.gslis@gmail.com
    # Adding text up
    text = email_utils.gen_email_text_grade(addr_from, addr_to, subj, *bcc, **email_info)
    return text


if __name__ == "__main__":

    week_start = datetime.datetime.now().date() - datetime.timedelta(days=29)
    week_start = time.mktime(week_start.timetuple())
    week_end = datetime.datetime.now().date() - datetime.timedelta(days=22)
    week_end = time.mktime(week_end.timetuple())-1

    week_start_ymd = utils.get_date_ymd(week_start) #e.g. 2017/12/17
    week_end_ymd = utils.get_date_ymd(week_end)

    # year version
    YEAR = '2017'
    # pbworks_db config
    PB_DB_USERNAME = 'root'
    PB_DB_PWD = 'root'
    PB_DB_HOST = 'localhost'
    PB_DB_NAME = 'pbworks_db'
    # log file path
    LOGFILE = '/Users/joseph/work/ra/rebuild/send_mail/logs/pbworks.log'
    # email txt files directory
    EMAIL_DIR = '/Users/joseph/work/ra/rebuild/send_mail/email-text/'
    CHARSET = 'utf8mb4'

    db_config = {
        'user': PB_DB_USERNAME,
        'password': PB_DB_PWD,
        'host': PB_DB_HOST,
        'database': PB_DB_NAME,
        'charset': CHARSET
    }

    # Connect to pbworks_db database
    conn = db_utils.connect_db(db_config)
    db_utils.db_exec(conn, 'use {}'.format(PB_DB_NAME))

    # fetch class_id
    sql_get_class_list = """ SELECT DISTINCT(class_id)
                                    FROM Class_user
                                    WHERE Class_user.class_id LIKE '{}%'
                                    AND Class_user.role = 'teacher'
                                    AND Class_user.active_email = 1""".format(YEAR)

    class_list = db_utils.db_exec(conn, sql_get_class_list)

    grade = str(class_list[0][0])[:-1]


    # Get a teacher list
    sql_get_teacher_list = """	SELECT loginUser.email, loginUser.user, loginUser.full_name
                                    FROM loginUser, Class_user
                                    WHERE loginUser.user = Class_user.name
                                    AND Class_user.role = 'teacher'
                                    AND Class_user.active_email = 1
                                    AND LENGTH(loginUser.email) > 5
                                    AND Class_user.class_id LIKE '{}{}'""".format(YEAR, 'pkps%')

    teacher_list = db_utils.db_exec(conn, sql_get_teacher_list)

    teacher_email = []
    teacher_username = []
    teacher_fullname = []

    for row in teacher_list:
        teacher_email.append(row[0])  # email address
        teacher_username.append(row[1])  # username
        teacher_fullname.append(row[2].encode('utf-8'))  # fullname

    # Loop through all teacher
    for num in range(len(teacher_email)):
        teacher_email_i = teacher_email[num]
        teacher_username_i = teacher_username[num]
        teacher_fullname_i = teacher_fullname[num]

        print ("teacher name: {0} teacher username: {1} teacher email: {2}".format(teacher_fullname_i, teacher_username_i,
                                                                                                      teacher_email_i))

        text = get_email_text(conn, class_list,grade, week_start, week_end, teacher_email_i, teacher_fullname_i)

        with open(EMAIL_DIR + grade + "_" + teacher_email_i + ".txt", "w") as text_file:
            text_file.write(text)
        text_file.close()




