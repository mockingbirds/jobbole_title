# -*- coding: utf-8 -*-
import re
import datetime

create_time = '2015/05/27'
create_time = datetime.datetime.strptime(create_time, '%Y/%m/%d').date()
print(create_time)