#!/usr/bin/python
# -*- coding: utf-8 -*-


def class_summary(cur,class_name_i,week_start,week_end,language):
    cur.execute(""" select Wiki_id,Group_index,No_of_plag
                    from Group_Stats
                    where class_id= '%s'
                    order by Group_index"""%class_name_i)
    group_plag_cnt_list = cur.fetchall()

    sum=0
    if len(group_plag_cnt_list)==0:
        return ""

    group_most_plag=group_plag_cnt_list[0]
    for group in group_plag_cnt_list:
        sum=sum+group[2]
        if group[2]>=group_most_plag[2]:
            group_most_plag=group
    group_plag_cnt_avg=sum/len(group_plag_cnt_list)

    if language=='english':
        title=u"\n<u><b>Plagiarism summary</b></u><br>"
        p1=u"Total number: "+str(sum)+"<br>"
        p2=u"Average per group : "+str(group_plag_cnt_avg)+"<br>"
        p3=u"Number of plagiarism in every group:<p style=\"padding-left:3em;margin:2px;\">"
        for group in group_plag_cnt_list:
            group_index=group[1]
            no_of_plag=group[2]
            text=u'Group '+str(group_index)+': '+str(no_of_plag)+'<br>'
            p3+=text
        p3+='</p>'
    elif language=='chinese':
        title=u"\n<u><b>抄袭句子统计</b></u><br>"
        p1=u"总数量："+str(sum)+"<br>"
        p2=u"平均数量："+str(group_plag_cnt_avg)+"<br>"
        p3=u'每小组抄袭句子数量：<p style=\"padding-left:3em;margin:2px;\">'
        for group in group_plag_cnt_list:
            group_index=group[1]
            no_of_plag=group[2]
            text=u'组 '+str(group_index)+': '+str(no_of_plag)+'<br>'
            p3+=text
        p3+='</p>'
    else:
        print 'Unsupported language'
        return ""

    summary_text=title+p1+p2+p3+'</br>'
    return summary_text
