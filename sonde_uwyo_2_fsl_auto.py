#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datetime
from datetime import datetime
import numpy as np
from siphon.simplewebservice.wyoming import WyomingUpperAir


# In[ ]:


outfile = ('C:/Users/lisad/Documents/Automation/realtime/sonde.fsl')
dt = datetime.today()
newdt = dt.replace(hour=12)
# Get current date and time, but change the hour to 12 so it will search for the 12z sonde
# If I use datetime.today w/out changng the hour it will search for a file from the current hour, which doesn't work for this purpose
station = 'DNR'


# In[ ]:


newdt


# In[ ]:


# Read in Univ of Wyoming sounding data based on time (newdt) and station
df = WyomingUpperAir.request_data(newdt, station)


# In[ ]:


df


# In[ ]:


#Extract year, month, day, and hour for header lines
df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day'] = df['time'].dt.day
df['hour'] = df['time'].dt.hour


# In[ ]:


year = df['year'].iloc[0]
month = df['month'].iloc[0].astype(str)
day = df['day'].iloc[0]
hour = df['hour'].iloc[0]


# In[ ]:


# Convert month number to 3-letter month name, for the header
month_num = month
datetime_object = datetime.strptime(month_num, "%m")
month_name = datetime_object.strftime("%b")


# In[ ]:


# FSL format is all caps
month_name.upper()


# month_name

# In[ ]:


# Extract the columns needed to write out in FSL format
df_out = df[['pressure','height','temperature','dewpoint','direction','speed']]


# In[ ]:


df_out


# In[ ]:


# should I create new columns and drop the old so I don't get the copy of a slice error?
# if I add .loc to each side, I don't get the error, but I also don't get the * 10 operation
# adding .copy() didn't help either, but I could have put it in the wrong place
# FSL format expects these units
df_out['pressure'] = df_out['pressure']*10
df_out['temperature'] = df_out['temperature']*10
df_out['dewpoint'] = df_out['dewpoint']*10


# In[ ]:


df_out


# In[ ]:


# change nans to 99999 per FSL format
df_out = df_out.fillna(99999).astype(int)


# In[ ]:


df_out


# In[ ]:


# assign all sonde levels to 6, apply logic below to change as needed
df_out['level'] = 6


# In[ ]:


# change bottom level (surface) to 9
df_out['level'].iloc[0] = 9
# change mandatory levels, as specified by pressure, to 4
# not bothering with levels above 500 hPa - aermet will drop anyway
df_out.loc[df_out.pressure == 10000, "level"] = 4
df_out.loc[df_out.pressure == 9250, "level"] = 4
df_out.loc[df_out.pressure == 8500, "level"] = 4
df_out.loc[df_out.pressure == 7000, "level"] = 4
df_out.loc[df_out.pressure == 5000, "level"] = 4
# change no wind levels to 5
df_out.loc[df_out.direction == 99999, "level"] = 5
# how to avoid copy of a slice error?


# In[ ]:


# reorder the columns so levels is first column (as needed for FSL format)
cols = df_out.columns.tolist()
cols = cols[-1:] + cols[:-1]
cols
df_out = df_out[cols]


# In[ ]:


df_out


# In[ ]:


# Need numpy array for header1 and header2 formatting
header1 =np.array([254, hour, day, '', month_name.upper(), year])


# In[ ]:


header1


# In[ ]:


# fudging the release time as 1103 since we'll only be reading in the 12z sondes
# and so far I don't see a way to capture the real release time 
header2 = np.array([1,  23062,  72469,  '39.77','N', '104.88','W',  1611, 1103])


# In[ ]:


header2


# In[ ]:


#need to calculate number of rows in the sonde, including the 4 header rows and the 3 mandatory rows I'm writing in
rows = df_out.shape[0] + 7


# In[ ]:


header3 = [2,99999,99999,99999,rows,99999,99999]


# In[ ]:


header3


# In[ ]:


header4 = [3,'       ','DNR', '       ','       ',11, 'kt']


# In[ ]:


header4


# In[ ]:


#Write the 4 header lines included in the FSL format
#Have to fudge some of them with 99999s
f=open(outfile,'w')
# the minus sign in front of the 4s is for left justified - to make the month line up correctly
fmt = '%7s','%7s','%7s','%6s','%-4s','%7s'
np.savetxt(f, header1.reshape((1,6)), fmt=fmt, delimiter="")
fmt = '%7s','%7s','%7s','%7s','%1s','%6s','%1s','%6s','%7s'
np.savetxt(f, header2.reshape((1,9)), fmt=fmt, delimiter="")
np.savetxt(f, header3, fmt='%7i', newline="")
f.write("\n")
np.savetxt(f, header4, fmt='%7s', newline="")
f.write("\n")


# In[ ]:


#Write the surface line - the first full line
np.savetxt(f, df_out.values[:1], fmt='%7i', delimiter="")


# In[ ]:


# add the 3 mandatory below ground levels here 10000, 9250, and 8500
# fudge some variables since I can't calculate with what was downloaded
mandatory1 = [4,10000,99999,99999,99999,99999,99999]
mandatory2 = [4,9250,99999,99999,99999,99999,99999]
mandatory3 = [4,8500,99999,99999,99999,99999,99999]
np.savetxt(f, mandatory1, fmt='%7s', newline="")
f.write("\n")
np.savetxt(f, mandatory2, fmt='%7s', newline="")
f.write("\n")
np.savetxt(f, mandatory3, fmt='%7s', newline="")
f.write("\n")


# In[ ]:


#Write the rest of the sonde - after the last mandatory row
np.savetxt(f, df_out.values[1:], fmt='%7i', delimiter="")


# In[ ]:


f.close()


# In[ ]:




