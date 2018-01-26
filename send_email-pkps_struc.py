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

def gen_email_by_classid(conn, class_id, week_start, week_end, teacher_email_i, teacher_fullname_i):

    # This part calculats the average value of the revision counts of each group in a class
    # Get a list of group number
    sql_get_class_group_list = "SELECT group_no FROM Wiki WHERE class_name = '{}'".format(class_id)
    class_group_list = db_utils.db_exec(conn, sql_get_class_group_list)

    no_of_groups = len(class_group_list)

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

    group_rev_cnt_list.sort(key=lambda x: x[1])  # order by 2nd column @revision_count ASC

    # Append zero to the remaining group
    if len(group_rev_cnt_list) < no_of_groups:
        group_rev_cnt_list = assign_zero(class_group_list, group_rev_cnt_list)


    best_group_comp = get_best_group_comp(group_rev_cnt_list, 3)
    worst_group_comp = get_worst_group_comp(group_rev_cnt_list, no_of_groups, 3)
    stat = get_stat(group_rev_cnt_list)

    # This part is to get the Best 5 and Worst 5 students in a class by comparing their word changes
    # Get a list all students
    sql_get_user_list = """ SELECT u.user_id, u.full_name, u.username, u.perm
                                    FROM User_wiki AS uw
                                    LEFT OUTER JOIN User AS u
                                        ON u.user_id = uw.uid
                                    INNER JOIN Wiki AS w
                                        ON uw.wiki_id = w.wiki_id
                                    WHERE w.class_name = '{}'
                                    AND u.perm = 'write'
                                    AND u.username IS NOT NULL
                                    ORDER BY u.perm""".format(class_id)

    user_list = db_utils.db_exec(conn, sql_get_user_list)

    no_of_students = len(user_list)

    # Get a list of the Best and Worst 5 students
    sql_get_result_of_stu = """SELECT User_id, User_name, User_no, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change)
                                        FROM Revision_Stats, Page, Wiki
                                        WHERE Revision_Stats.page_id = Page.Page_id
                                        AND Page.wiki_id = Wiki.wiki_id
                                        AND Wiki.class_name = '{0}'
                                        AND Revision_creation_time BETWEEN '{1}' AND '{2}'
                                        AND User_perm = 'write'
                                        GROUP BY User_id
                                        ORDER BY SUM(Words_change)""".format(class_id, week_start, week_end)

    stu_rev_cnt_list = db_utils.db_exec(conn, sql_get_result_of_stu)

    best_indiv_comp = get_best_indiv_comp(stu_rev_cnt_list, 5)
    worst_indiv_comp = get_worst_indiv_comp(stu_rev_cnt_list, 5)



    teacher_email_i = 'josephchuh7@gmail.com'

    addr_from = 'wikiglass@ccmir.cite.hku.hk'
    addr_to = teacher_email_i
    subj = 'Weekly Summary'
    bcc = ()

    email_info = {
        'teacher_fullname': teacher_fullname_i,
        'class_name': class_id,
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
    text = email_utils.gen_email_text(addr_from, addr_to, subj, *bcc, **email_info)

    with open(EMAIL_DIR + class_id + "_" + teacher_email_i + ".txt", "w") as text_file:
        text_file.write(text)
    text_file.close()

# @num : the number of groups to show
# e.g. for "Top 3 groups", num should be 3
def get_best_group_comp(group_rev_cnt_list, num):

    len_group_rev_cnt_list = len(group_rev_cnt_list)

    if len_group_rev_cnt_list < num:
        num = len_group_rev_cnt_list

    best_group = []

    # Get a list of the best 3 groups
    for i in range(len_group_rev_cnt_list - 1, len_group_rev_cnt_list - 1 - num, -1):
        if group_rev_cnt_list[i][1] != 0:
            best_group.append(group_rev_cnt_list[i])

    best_group_no = []
    best_group_rev_count = []

    # Output Best 3 groups
    len_best_group = len(best_group)
    for row in best_group:
        best_group_no.append(row[0])
        best_group_rev_count.append(row[1])

    return email_utils.get_best_group_comp(len_best_group, best_group_no, best_group_rev_count)

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

# @num : the number of students to show
# e.g. for "Top 3 students", num should be 3
def get_best_indiv_comp(stu_rev_cnt_list, num):

    len_stu_rev = len(stu_rev_cnt_list)

    if len_stu_rev < num:
        num = len_stu_rev

    best_stu_list = []

    for i in range(0, num):
        best_stu_list.append(stu_rev_cnt_list[len_stu_rev - 1 - i])

    # Output Best 5 students
    best_stu_info = email_utils.get_best_stu_info(best_stu_list)
    return  email_utils.get_best_indiv_comp(**best_stu_info)

def get_worst_indiv_comp(stu_rev_cnt_list, num):

    len_stu_rev = len(stu_rev_cnt_list)

    if len_stu_rev < num:
        num = len_stu_rev

    worst_stu_list = []

    for i in range(0, num):
        worst_stu_list.append(stu_rev_cnt_list[i])

    zero_stu_list = []

    for row in stu_rev_cnt_list:
        if row[7] == 0:
            zero_stu_list.append(row[1])

    worst_stu_info = email_utils.get_worst_stu_info(worst_stu_list)

    return email_utils.get_worst_indiv_comp(zero_stu_list, **worst_stu_info)

def get_stat(group_rev_cnt_list):
    group_rev_count = []

    for row in group_rev_cnt_list:
         group_rev_count.append(row[1])

    return email_utils.get_stat(group_rev_count)


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
        class_name = []

        # fetch class_id
        sql_get_teacher_class_list = """ SELECT DISTINCT(class_id)
                                    FROM Class_user
                                    WHERE name = '{}'
                                    AND Class_user.class_id LIKE '{}%'
                                    AND Class_user.role = 'teacher'
                                    AND Class_user.active_email = 1""".format(teacher_username_i, YEAR)

        teacher_class_list = db_utils.db_exec(conn, sql_get_teacher_class_list)

        for row in teacher_class_list:
            class_name.append(row[0])
            print("class_id: " + row[0])

        for row in class_name:
            class_id = row.encode("utf-8")
            gen_email_by_classid(conn, class_id, week_start, week_end, teacher_email_i, teacher_fullname_i)