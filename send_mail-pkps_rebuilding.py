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
    'user' : PB_DB_USERNAME,
    'password' : PB_DB_PWD,
    'host' : PB_DB_HOST,
    'database' : PB_DB_NAME,
    'charset' : CHARSET
}

logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

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

teacher_email=[]
teacher_username=[]
teacher_fullname=[]

for row in teacher_list:
    teacher_email.append(row[0])  # email address
    teacher_username.append(row[1])   # username
    teacher_fullname.append(row[2].encode('utf-8'))   #fullname

# week_start = datetime.datetime.now().date() - timedelta(days=7)
# week_start = time.mktime(week_start.timetuple())
# week_end = datetime.datetime.now().date()
# week_end = time.mktime(week_end.timetuple())-1

week_start = datetime.datetime.now().date() - datetime.timedelta(days=29)
week_start = time.mktime(week_start.timetuple())
week_end = datetime.datetime.now().date() - datetime.timedelta(days=22)
week_end = time.mktime(week_end.timetuple())-1

year = YEAR

# Loop through all teacher
for num in range(len(teacher_email)):
    teacher_email_i = teacher_email[num]
    teacher_username_i = teacher_username[num]
    teacher_fullname_i = teacher_fullname[num]

    print ("teacher name: {0} teacher username: {1} teacher email: {2}".format(teacher_fullname_i, teacher_username_i, teacher_email_i))

    class_name=[]

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

    #class_name stores all class_id
    # Loop through all classes
    for class_name_i in class_name:
        # Arrays storing revision counts of all groups
        group_rev_no = []  # no. of groups that have revisions
        group_rev_count=[]

        # Arrays storing best 3 and worst 3 groups in revision counts
        best_group_no=[]
        best_group_rev_count=[]
        worst_group_no=[]
        worst_group_rev_count=[]

        # Arrays storing best 5 and worst 5 students in word changes
        best_stu_name=[]
        best_stu_add=[]
        best_stu_del=[]
        worst_stu_name=[]
        worst_stu_add=[]
        worst_stu_del=[]

        # This part calculats the average value of the revision counts of each group in a class
        # Get a list of group number
        sql_get_class_group_list = "SELECT group_no FROM Wiki WHERE class_name = '{}'".format(class_name_i)
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
                                        GROUP BY group_no""".format(class_name_i, week_start, week_end)
        group_rev_cnt_list = db_utils.db_exec(conn, sql_get_rev_cnt_list)

        count = no_of_groups

        # Check if the group made any revisions; If made no revision, isNull=True
        #if count == no_of_groups:
        if len(group_rev_cnt_list) == 0:
            is_null = True  # 所有小组都没有revision的情况
        else:
            is_null = False

        # Append zero to the remaining group
        if len(group_rev_cnt_list) < no_of_groups:
            group_rev_cnt_list = assign_zero(class_group_list, group_rev_cnt_list)

        for row in group_rev_cnt_list:  # group_rev_cnt_list is a 2D-list
             group_rev_no.append(row[0])
             group_rev_count.append(row[1])

        # Output for this part
        if is_null:
            stat="Not a single group made any revisions this week. Please consider encouraging students to contribute more actively.</p>"
        else:
            avg = utils.mean(group_rev_count)
            sd = utils.stdev(group_rev_count)
            stat = "In this class, the average number of revisions per group is " + str(avg) + ". Following is a brief analysis of weekly performance of the class.</p>"
            print(str(sum(group_rev_count)) + " " + str(avg) + " " + str(sd))


        # This part is to get the Best 3 and Worst 3 groups in a class by comparing their revision counts
        # No need to fetch data from db here, @group_rev_cnt_list contains all group numbers with there revision counts.
        group_rev_cnt_list.sort(key=lambda x: x[1]) #order by 2nd column @revision_count AS

        num = 3
        len_group_rev_cnt_list = len(group_rev_cnt_list)
        if len_group_rev_cnt_list < num :
            num = len_group_rev_cnt_list

        best_group = []
        worst_group = []
        # Get a list of the best 3 groups
        for i in range(len_group_rev_cnt_list - 1, len_group_rev_cnt_list - 1 - num, -1):
            if group_rev_cnt_list[i][1] != 0:
                best_group.append(group_rev_cnt_list[i])
        # Get a list of the worst 3 groups
        for i in range(0, num):
            if group_rev_cnt_list[i][1] != 0:
                worst_group.append(group_rev_cnt_list[i])

        del len_group_rev_cnt_list

        # Output Best 3 groups
        len_best_group = len(best_group)
        for row in best_group:
            best_group_no.append(row[0])
            best_group_rev_count.append(row[1])

        if len_best_group==3:
            best_group_comp = "<u><b>Group comparsion</u><br>Top 3 groups with the most revisions:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(best_group_no[0]) \
                        +" ("+str(best_group_rev_count[0])+" revisions)<br>2. Group "+str(best_group_no[1])+" ("+str(best_group_rev_count[1]) \
                        +" revisions)<br>3. Group "+str(best_group_no[2])+" ("+str(best_group_rev_count[2])+" revisions)</p>"
        elif len_best_group==2:
            best_group_comp = "<u><b>Group comparsion</u><br>Top 2 groups with the most revisions:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(best_group_no[0]) \
                        +" ("+str(best_group_rev_count[0])+" revisions)<br>2. Group "+str(best_group_no[1])+" ("+str(best_group_rev_count[1]) \
                        +" revisions)</p>"
        elif len_best_group==1:
            best_group_comp = "<u><b>Group comparsion</u><br>The only group made revision:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(best_group_no[0]) \
                        +" ("+str(best_group_rev_count[0])+" revisions)</p>"
        else:
            best_group_comp = ""

        # Output Worst 3 groups
        zero = []  # all groups with zero revision counts
        for row in worst_group:
            worst_group_no.append(row[0])
            worst_group_rev_count.append(row[1])

        for row in group_rev_cnt_list:
            if row[1] == 0:
                zero.append(row)

        count = len(zero)  # count: number of groups with zero revision counts

        if count==0:
            worst_group_comp = "3 groups with the fewest revisions:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(worst_group_no[0]) \
                +" ("+str(worst_group_rev_count[0])+" revisions)<br>2. Group "+str(worst_group_no[1])+" ("+str(worst_group_rev_count[1]) \
                +" revisions)<br>3. Group "+str(worst_group_no[2])+" ("+str(worst_group_rev_count[2])+" revisions)</p><br>"
        elif count==1:
            worst_group_comp = "3 groups with the fewest revisions:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(zero[0][0]) \
                +" (0 revisions)<br>2. Group "+str(worst_group_no[0])+" ("+str(worst_group_rev_count[0]) \
                +" revisions)<br>3. Group "+str(worst_group_no[1])+" ("+str(worst_group_rev_count[1])+" revisions)</p><br>"
        elif count==2:
            worst_group_comp = "3 groups with the fewest revisions:<p style=\"padding-left:3em;margin:2px;\">1. Group "+str(zero[0][0]) \
                +" (0 revisions)<br>2. Group "+str(zero[1][0])+" (0 revisions)<br>3. Group " \
                +str(worst_group_no[0])+" ("+str(worst_group_rev_count[0])+" revisions)</p><br>"
        elif count==no_of_groups:
            worst_group_comp = ""
        else:
            worst_group_comp = "Groups without making any revisions:<p style=\"padding-left:3em;margin:2px;\">"
            for i in range(1,count-1):
                worst_group_comp = worst_group_comp+str(i)+". Group "+str(zero[i-1][0])+"<br>"
            worst_group_comp = worst_group_comp+str(count-1)+". Group "+str(zero[count-2][0])+"<br>"
            worst_group_comp = worst_group_comp+str(count)+". Group "+str(zero[count-1][0])+"</p><br>"


        # This part is to get the Best 5 and Worst 5 students in a class by comparing their word changes
        # Get a list all students
        # cur.execute("""SELECT u.user_id, u.full_name, u.username, u.perm
            # 			FROM User_wiki AS uw
            # 			LEFT OUTER JOIN User AS u
            # 				ON u.user_id = uw.uid
            # 			INNER JOIN Wiki AS w
            # 				ON uw.wiki_id = w.wiki_id
            # 			WHERE w.class_name = %s
            # 			AND u.perm = 'write'
            # 			AND u.username IS NOT NULL
            # 			ORDER BY u.perm""",(class_name_i ,))
        # user_list = cur.fetchall()

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
                                ORDER BY u.perm""".format(class_name_i)

        user_list = db_utils.db_exec(conn, sql_get_user_list)

        no_of_students = len(user_list)

        # Get a list of the Best and Worst 5 students
        # cur.execute("""SELECT User_id, User_name, User_no, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change)
        # 							FROM Revision_Stats, Page, Wiki
        # 							WHERE Revision_Stats.page_id = Page.Page_id
        # 							AND Page.wiki_id = Wiki.wiki_id
        # 							AND Wiki.class_name = %s
        # 							AND Revision_creation_time BETWEEN %s AND %s
        # 							AND User_perm = 'write'
        # 							GROUP BY User_id
        # 							ORDER BY SUM(Words_change)""",(class_name_i, week_start, week_end,))
        # result_of_stu = cur.fetchall()

        # Get a list of the Best and Worst 5 students
        sql_get_result_of_stu = """SELECT User_id, User_name, User_no, User_perm, COUNT(*), SUM(Words_addition), SUM(Words_deletion), SUM(Words_change)
                                    FROM Revision_Stats, Page, Wiki
                                    WHERE Revision_Stats.page_id = Page.Page_id
                                    AND Page.wiki_id = Wiki.wiki_id
                                    AND Wiki.class_name = '{0}'
                                    AND Revision_creation_time BETWEEN '{1}' AND '{2}'
                                    AND User_perm = 'write'
                                    GROUP BY User_id
                                    ORDER BY SUM(Words_change)""".format(class_name_i, week_start, week_end)

        result_of_stu = db_utils.db_exec(conn, sql_get_result_of_stu)

        len_result = len(result_of_stu)
        best = []
        worst = []

        for i in range(0, 5):
            worst.append(result_of_stu[i])
            best.append(result_of_stu[len_result - 1 - i])

        #del len_result

        # Output Best 5 students
        user_of_page = []
        count = 0
        for row in best:
            user_name = row[1].encode('utf-8')
            total_a = row[5]
            total_d = row[6]
            best_stu_name.append(user_name)
            best_stu_add.append(total_a)
            best_stu_del.append(total_d)
            count = count + 1

        if count>=2:
            best_indiv_comp = u"\n<u><b>Individual performance</u><br>Top "+str(count)+" students with the most contributions:<p style=\"padding-left:3em;margin:2px;\">"
            for i in range(1,count-1):
                best_indiv_comp = best_indiv_comp+str(i)+". "+str(best_stu_name[i-1]).title()+" ("+str(best_stu_add[i-1])+" words added, "+str(best_stu_del[i-1])+" words deleted)<br>"
            best_indiv_comp = best_indiv_comp+str(count-1)+". "+str(best_stu_name[count-2]).title()+" ("+str(best_stu_add[count-2])+" words added, "+str(best_stu_del[count-2])+" words deleted)<br>"
            best_indiv_comp = best_indiv_comp+str(count)+". "+str(best_stu_name[count-1]).title()+" ("+str(best_stu_add[count-1])+" words added, "+str(best_stu_del[count-1])+" words deleted)<br></p>"
        elif count==1:
            best_indiv_comp = "\n<u><b>Individual performance</u><br>The top student with the most contribution is<p style=\"padding-left:3em;margin:2px;\">"
            best_indiv_comp = best_indiv_comp+"1. "+str(best_stu_name[0]).title()+" ("+str(best_stu_add[0])+" words added, "+str(best_stu_del[0])+" words deleted).<br></p>"
        else:
            best_indiv_comp = u""

        # Output Worst 5 students
        user_of_page = []
        zero = []
        for row in worst:
            if row[7] != 0:
                user_of_page.append(row[0])
                worst_stu_name.append(row[1].encode('utf-8'))
                worst_stu_add.append(row[5])
                worst_stu_del.append(row[6])
        print(str(no_of_students) + " === " + str(len(user_of_page)))

        for row in result_of_stu:
            if row[7] == 0:
               zero.append(row[1])

        count = len(zero)  # count: number of students with zero revision counts

        if count==0:
            worst_indiv_comp = u"\n5 students with the fewest contributions:<p style=\"padding-left:3em;margin:2px;\">1. "+str(worst_stu_name[0]).title() \
                +" ("+str(worst_stu_add[0])+" words added, "+str(worst_stu_del[0])+" words deleted)<br>2. "+str(worst_stu_name[1]).title()+" ("+str(worst_stu_add[1]) \
                +" words added, "+str(worst_stu_del[1])+" words deleted)<br>3. "+str(worst_stu_name[2]).title()+" ("+str(worst_stu_add[2])+" words added, " \
                +str(worst_stu_del[2])+" words deleted)<br>4. "+str(worst_stu_name[3]).title()+" ("+str(worst_stu_add[3])+" words added, "+str(worst_stu_del[3]) \
                +" words deleted)<br>5. "+str(worst_stu_name[4]).title()+" ("+str(worst_stu_add[4])+" words added, "+str(worst_stu_del[4])+" words deleted)</p><br>"
        elif count==1:
            worst_indiv_comp = u"\n5 students with the fewest contributions:<p style=\"padding-left:3em;margin:2px;\">1. "+str(zero[0]).title() \
                +" (0 words added, 0 words deleted)<br>2. "+str(worst_stu_name[0]).title()+" ("+str(worst_stu_add[0]) \
                +" words added, "+str(worst_stu_del[0])+" words deleted)<br>3. "+str(worst_stu_name[1]).title()+" ("+str(worst_stu_add[1])+" words added, " \
                +str(worst_stu_del[1])+" words deleted)<br>4. "+str(worst_stu_name[2]).title()+" ("+str(worst_stu_add[2])+" words added, "+str(worst_stu_del[2]) \
                +" words deleted)<br>5. "+str(worst_stu_name[3]).title()+" ("+str(worst_stu_add[3])+" words added, "+str(worst_stu_del[3])+" words deleted)</p><br>"
        elif count==2:
            worst_indiv_comp = u"\n5 students with the fewest contributions:<p style=\"padding-left:3em;margin:2px;\">1. "+str(zero[0]).title() \
                +" (0 words added, 0 words deleted)<br>2. "+str(zero[1]).title()+" (0 words added, 0 words deleted)<br>3. "+str(worst_stu_name[0]).title() \
                +" ("+str(worst_stu_add[0])+" words added, "+str(worst_stu_del[0])+" words deleted)<br>4. "+str(worst_stu_name[1]).title()+" ("+str(worst_stu_add[1]) \
                +" words added, "+str(worst_stu_del[1])+" words deleted)<br>5. "+str(worst_stu_name[2]).title()+" ("+str(worst_stu_add[2])+" words added, " \
                +str(worst_stu_del[2])+" words deleted)</p><br>"
        elif count==3:
            worst_indiv_comp = u"\n5 students with the fewest contributions:<p style=\"padding-left:3em;margin:2px;\">1. "+str(zero[0]).title()\
                +" (0 words added, 0 words deleted)<br>2. "+str(zero[1]).title()+" (0 words added, 0 words deleted)<br>3. "+str(zero[2]).title()+" (0 words added, " \
                +"0 words deleted)<br>4. "+str(worst_stu_name[0]).title()+" ("+str(worst_stu_add[0])+" words added, "+str(worst_stu_del[0]) \
                +" words deleted)<br>5. "+str(worst_stu_name[1]).title()+" ("+str(worst_stu_add[1])+" words added, "+str(worst_stu_del[1])+" words deleted)</p><br>"
        elif count==4 and no_of_students > 4:
            worst_indiv_comp = u"\n5 students with the fewest contributions:<p style=\"padding-left:3em;margin:2px;\">1. "+str(zero[0]).title() \
                +" (0 words added, 0 words deleted)<br>2. "+str(zero[1]).title()+" (0 words added, 0 words deleted)<br>3. "+str(zero[2]).title()+" (0 words added, " \
                +"0 words deleted)<br>4. "+str(zero[3]).title()+" (0 words added, 0 words deleted)<br>5. " \
                +str(worst_stu_name[0]).title()+" ("+str(worst_stu_add[0])+" words added, "+str(worst_stu_del[0])+" words deleted)</p><br>"
        elif count == no_of_students:
            worst_indiv_comp = u""
        else:
            worst_indiv_comp = u"\nStudents without making any revisions:<p style=\"padding-left:3em;margin:2px;\">"
            for i in range(1,count-1):
                worst_indiv_comp = worst_indiv_comp+str(i)+". "+str(zero[i-1]).title()+"<br>"
            worst_indiv_comp = worst_indiv_comp+"\n"+str(count-1)+". "+str(zero[count-2]).title()+"<br>"
            worst_indiv_comp = worst_indiv_comp+str(count)+". "+str(zero[count-1]).title()+"</p><br>"

        #plag_summary=plag_summary.class_summary(cur,class_name_i,0,0,'english')

        teacher_email_i = 'josephchuh7@gmail.com'

        #Bcc: ecswikis@gmail.com, xh.gslis@gmail.com
        # Adding text up
        text = "From: wikiglass@ccmir.cite.hku.hk\nTo: " \
               + teacher_email_i \
               + "\nBcc:" + "\nContent-Type: text/html\nSubject: Weekly Summary - " + class_name_i + "\n\n" \
               + "<html><head><title>Weekly Summary</title></head>" + "<body>Dear " + teacher_fullname_i + ",<p><br>This is a weekly summary (" + datetime.datetime.fromtimestamp(
            week_start).strftime('%Y/%m/%d') \
               + " - " + datetime.datetime.fromtimestamp(week_end).strftime(
            '%Y/%m/%d') + ") of students' performance in Class " \
               + class_name_i[
                 -2:] + ". " + stat + best_group_comp + worst_group_comp + best_indiv_comp + worst_indiv_comp \
               + "Please log in to <a href='http://ccmir.cite.hku.hk/wikiglass/'>Wikiglass Site</a> for more details at any time. Data on Wikiglass are updated everyday.<p><br>" \
               + "Yours sincerely,<br>Wikiglass</body></html>\n\n"
        with open(EMAIL_DIR + class_name_i + "_" + teacher_email_i + ".txt", "w") as text_file:
            text_file.write(text)
        text_file.close()





