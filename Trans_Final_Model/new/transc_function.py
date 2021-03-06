
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 10:23:08 2019

@author: tarun.bhavnani@dev.smecorner.com
"""
import pandas as pd
import os
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from time import time
from keras.models import model_from_json
import pickle
from keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import os
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from time import time
import datetime
from sklearn import preprocessing
import matplotlib.pyplot as plt



"""
converting all the misread/mis spelled to the correct ones. like IMPS may be 1mps and so on.
After this removing the special characters which can be removed .
Removing extra spaces
Now we use the basic knowledge to classify using regex.
Basic knowledge as in if it says imps then it is imps.
say atm wdl it is cash and so on.
The catch is the positionong of these conversions. like therse is cash written in lots of cheques and
other classes. So we classify cash first, and then if it is overwritten by some other class its 
still correct.
The ones which are left are manually tagged and then a deep learniong model is fit in
for training.


"""
def clean_transc(dat):
  #have removed the spaces from imps and rtgs as in neft, see
  t0= time()
  dat["Des"] = [str(i) for i in dat["Description"]]
  dat["Des"]=" "+dat["Des"]+" "
  dat["Des"] = dat["Des"].apply(lambda x: x.lower())
  dat["Des"]=[re.sub("[i|1]/w"," inwards ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("[o|0]/w"," outwards ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("b/f"," brought_fwd ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("neft"," neft ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("[i|1]mp[s|5]"," imps ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub(r'r[i|t|1][g|8][s|5]'," rtgs ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("ecs"," ecs ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("cash"," cash ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("nach"," nach ",i) for i in dat["Des"]]
  #dat["Des"]=[re.sub("ebank","ebank",i) for i in dat["Des"]]
  dat["Des"]=[re.sub(r"c[o|0][1|l][1|l]","coll",i) for i in dat["Des"]]# for int.co11
  dat["Des"]=[re.sub("vvdl","wdl",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("nfs","nfs",i) for i in dat["Des"]]
  dat["Des"]=[re.sub(r"[1|l][o|0]an"," loan ",i) for i in dat["Des"]]
  dat["Des"]=[re.sub("[\n]|[\r]"," ",i) for i in dat["Des"]]


  dat["Des"]=[re.sub(r"\(|\)|\[|\]"," ",i) for i in dat["Des"]]#brackets

  dat["Des"]=[re.sub("-|:|\.|/"," ",i) for i in dat["Des"]]


  dat["Des"]=[re.sub("a c ","ac ", i) for i in dat["Des"]]




  dat["Des_cl"]= [re.sub(" ","",i) for i in dat["Des"]]

  #########################################################################
  "Classification"



  dat["classification"]="Not_Tagged"
  # si as transfer
  dat["classification"]=["transfer" if len(re.findall(r"\bsi\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  #dat["classification"]=["transfer" if len(re.findall(r"\bs i\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  dat["classification"]=["dd" if len(re.findall(r"\bdd\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  # ib also as transfer
  dat["classification"]=["ib" if len(re.findall(r"\bib\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  #ft as transfer 
  dat["classification"]=["transfer" if len(re.findall(r"\bft\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]


  dat["classification"]=["brought_fwd" if len(re.findall("brought_fwd",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]




  dat["classification"]=["transfer" if len(re.findall(r"\bdr\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["transfer" if len(re.findall(r"\bftr\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["transfer" if len(re.findall(r"\btpf[t|r]\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["transfer" if len(re.findall(r"\bfund[s]? trf\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["transfer" if len(re.findall(r"\bmob[\s]?tpft\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]  
  dat["classification"]=["transfer" if len(re.findall(r"\btrf\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]    
  dat["classification"]=["transfer" if len(re.findall("tpt",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  dat["classification"]=["transfer" if len(re.findall("transfer",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  
  
  dat["classification"]=["neft" if len(re.findall("neft",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["rtgs" if len(re.findall("rtgs",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]


  dat["classification"]=["imps" if len(re.findall(r"[i|1]mps",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["cash" if len(re.findall("cash",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  dat["classification"]=["cash" if len(re.findall("at[m|w]",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["cash" if len(re.findall("self",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["pos" if len(re.findall(r"\bpos\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  dat["classification"]=["pos" if len(re.findall(r"\bcard settlement\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  dat["classification"]=["pos" if len(re.findall("debitcard",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["cheque" if len(re.findall(r"che?q",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  dat["classification"]=["cheque" if len(re.findall("c[l|1][g|q]",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  dat["classification"]=["cheque" if len(re.findall(r"c[l|1]earing",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  
  #cheque for INF
  dat["classification"]=["cheque" if len(re.findall(r"\b[i|1]nf\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  #cash for mmt
  dat["classification"]=["cash" if len(re.findall(r"\bmmt\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  
  #ecs, nach, emi, loan are all nach/emi
  dat["classification"]=["nach/emi" if len(re.findall("ecs",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["nach/emi" if len(re.findall("loan",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["nach/emi" if len(re.findall(r"em[i|1|u]",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["nach/emi" if len(re.findall("nach",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["nach/emi" if len(re.findall(r"\bach\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  
  dat["classification"]=["i/w" if len(re.findall("inward",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  dat["classification"]=["o/w" if len(re.findall("outward",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  
  dat["classification"]=["i/w" if len(re.findall(r"iwclg",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  dat["classification"]=["o/w" if len(re.findall(r"owclg",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]

  dat["classification"]=["i/w" if len(re.findall(r"\biw\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["o/w" if len(re.findall(r"\bow\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]

  #see if we need owclg as a clg or a ow 
  #dat["classification"]=["i/w" if len(re.findall(r"\biw\b",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  #dat["classification"]=["o/w" if len(re.findall(r"\bow\b",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  
  #check for debit and credit here in int_coll
  dat["classification"]=["int_coll" if len(re.findall("int coll",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  dat["classification"]=["internet_banking" if len(re.findall(r"\bup[i|1]",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  dat["classification"]=["internet_banking" if len(re.findall(r"ebanking",x))>0 else y for x,y in zip(dat["Des_cl"], dat["classification"])]
  
  dat["classification"]=["tax" if len(re.findall(r"tax",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  dat["classification"]=["tax" if len(re.findall(r"\btds\b",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  
  dat["classification"]=["gst" if len(re.findall(r"[s|c]gst|\bgst",x))>0 else y for x,y in zip(dat["Des"], dat["classification"])]
  #charges!
  dat["cl_cl"]="Not_Tagged"
  dat["cl_cl"]=["charges" if len(re.findall(r"charge?",x))>0 else y for x,y in zip(dat["Des_cl"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall("chrg",x))>0 else y for x,y in zip(dat["Des_cl"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall(r"\bchgs?\b",x))>0 else y for x,y in zip(dat["Des_cl"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall("commission",x))>0 else y for x,y in zip(dat["Des_cl"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall(r"\bfee\b",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall(r"\bnftchg\b",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  dat["cl_cl"]=["charges" if len(re.findall(r"\bchg[s|\s]\b",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  #return
  #dat["cl_ret"]="Not_Tagged"
  #dat["cl_cl"]=["return" if len(re.findall(r"\bretu?r?n?|return",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  dat["cl_cl"]=["return" if len(re.findall(r"\bretu?r?n?\b|return",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  dat["cl_cl"]=["return" if len(re.findall(r"\brtn\b",x))>0 else y for x,y in zip(dat["Des"], dat["cl_cl"])]
  #dat["gst"]="Not_Tagged"
  #dat["classification"]=["gst" if len(re.findall(r"[s|c]gst|\bgst",x))>0 else y for x,y in zip(dat["Des"], dat["gst"])]
  
  #Merging classification, cl_cl and gst!
  #new modification
  
  dat["classification"]=[y if y!="Not_Tagged" else x for x,y in zip(dat["classification"], dat["cl_cl"])]
  #dat["classification"]=[y if y!="Not_Tagged" else x for x,y in zip(dat["classification"], dat["gst"])]
  
  
  #dat= dat.drop(labels=["cl_cl", "gst", "Des_cl"], axis=1)
  
  
  
  dat["Des"]=["".join([j for j in i if j.isdigit()==False ]) for i in dat["Des"]]



  #dat["Des"]=[" ".join([j for j in i.split() if not any(c.isdigit() for c in j)]) for i in dat["Des"]]
  #if any alpha numerics are still left

  dat["Des"]= [re.sub("[\W_]+"," ",i) for i in dat["Des"]]
  print("time taken:",time()-t0, "seconds")
  return(dat)


#fdf=clean_transc(fdf)

def pattern(dat):
#  from fuzzywuzzy import fuzz
#  from fuzzywuzzy import process

  
  def sortSecond(val): 
      return val[1]  

  
  dfg=pd.DataFrame( columns =['Debits', 'Credits']) 
  
  narrations = list(dat["Des"][dat["Credit"]==0])
  narrations=[' '.join(str(i).split()) for i in narrations]
  #jk=narrations
  #remove stopwords, to improve results
  stopwords= ["neft", "rtgs","imps","cash", "cheque", "tpt", "transfer", "to", "atm","dd","clg","atw","self","wdr","ecs","ach",]
  narrations=[" ".join([j for j in i.split() if j not in stopwords]) for i in narrations]
  list_groups_debit = []
  group_count = 0

  for i,string in enumerate(narrations):
    print(i)
   #if group_count>1000:
   #  break
   #else:
    #print(i,string)
    try:
    
      match_list = process.extract(string, narrations, scorer = fuzz.token_set_ratio, limit = len(narrations))     
      match_list = [ele[0] for ele in match_list if ele[1] >80]

      if len(match_list) > 5: #in list(range(2, 10)):
          list_groups_debit.append(tuple((match_list, len(match_list), group_count)))
          print(group_count)
          group_count +=1


      #for ele in match_list:
      #  narrations.remove(ele)
      narrations=[i for i in narrations if i not in match_list]
        #print("a")
      #print("cccccccccccccc")
    except:
      print("skipping",i,string)

 
  list_groups_debit.sort(key = sortSecond,reverse = True)
  

  dfg["Debits"]=pd.Series([(i[0][1],i[1]) for i in list_groups_debit[0:10]])
  #dfg["Debits-Counts"]=pd.Series([i[1] for i in list_groups_debit[0:10]])



  narrations = list(dat["Des"][dat["Debit"]==0])
  narrations=[' '.join(str(i).split()) for i in narrations]
  stopwords= ["neft", "rtgs","imps","cash", "cheque", "tpt", "transfer", "to", "atm","dd","clg","atw","self","wdr","ecs","ach",]
  narrations=[" ".join([j for j in i.split() if j not in stopwords]) for i in narrations]
  list_groups_credit = []
  group_count = 0

  
  for i,string in enumerate(narrations):
    try:
    #print(i,string)
      match_list = process.extract(string, narrations, scorer = fuzz.token_set_ratio, limit = len(narrations))     
      match_list = [ele[0] for ele in match_list if ele[1] >80]
      if len(match_list) > 5: #in list(range(2, 10)):
          list_groups_credit.append(tuple((match_list, len(match_list), group_count)))
          print(group_count)
          group_count +=1


      #for ele in match_list:
      #  narrations.remove(ele)
      narrations=[i for i in narrations if i not in match_list]
      #print("a")
      #print("cccccccccccccc")
    except:
      print("skipping",i,string)

#  def sortSecond(val): 
#      return val[1]  

  list_groups_credit.sort(key = sortSecond,reverse = True)

  #dfg["Credits"]=[i[0][1] for i in list_groups_credit[1:10]]
  dfg["Credits"]=pd.Series([(i[0][1],i[1]) for i in list_groups_credit[0:10]])
  #gh=[i[0][1] for i in list_groups_credit[1:10]]
  #[y if y else i for i,y in zip(dfg["Credits"],gh)]
  
  return(dfg)
  




def round_entry(dat):
 
 dat['DateTime'] = pd.to_datetime(dat['Date_new'])
 #dat.DateTime.iloc[1].day
 dat["day"]=dat.DateTime.apply(lambda x: x.day)
 dat["month"]=dat.DateTime.apply(lambda x: x.month)
 dat["year"]=dat.DateTime.apply(lambda x: x.year)
 dat["my"]= [str(i)+"-"+str(j) for i,j in zip(dat["year"], dat["month"])]
   
 dat["roundiw"]=0
 dat["roundow"]=0
 print("Finding round entries...")

 for i in range(0,len(dat)):
   #print(i,"of", len(dat))
   for j in range(i,i+5):
#    print(j)
     try:
         #debit and then credit
        
         if dat.Debit.iloc[i]==dat.Credit.iloc[j] and dat.Debit.iloc[i]!=0 :
           #print("check........ {}".format(i))
           dat['roundiw'].iloc[i]="inward debit suspected {}".format(i)
           dat['roundiw'].iloc[j]="inward credit suspected {}".format(i)
           if dat["Date_new"].iloc[i]==dat["Date_new"].iloc[j]: #for bounce
             dat['roundiw'].iloc[j]="inward credit suspected same date {}".format(i)

         if dat.Credit.iloc[i]==dat.Debit.iloc[j] and dat.Credit.iloc[i]!=0 :
           #print("check........ {}".format(i))
           dat['roundow'].iloc[i]="outward credit suspected {}".format(i)
           dat['roundow'].iloc[j]="outward debit suspected {}".format(i)
           if dat["Date_new"].iloc[i]==dat["Date_new"].iloc[j]: #for bounce
             dat['roundow'].iloc[j]="outward debit suspected same date{}".format(i)

            
     except:
       print("NA")
 #print(dat['roundiw'].value_counts())
 #print(dat['roundow'].value_counts())
 print("Round-Inwards-suspected Entries--->",sum([1 for i in dat.roundiw if i!=0]))
 print("Round-Outwards-suspected Entries--->",sum([1 for i in dat.roundow if i!=0]))
 
 df=pd.DataFrame(columns=["year","month","cr","dr","total_round","total_entries"], index=range(len(set(dat["my"]))))
 #df=pd.DataFrame(list(set(dat["year"])),columns=["year"])

 for i,my in enumerate(set(dat["my"])):
    print(i,my)
    
    df["year"][i]=my.split("-")[0]
    df["month"][i]=my.split("-")[1]

    df["dr"][i]=sum([1 for i in dat["roundiw"][dat["my"]==my] if i!=0])
    
    df["cr"][i]=sum([1 for i in dat["roundow"][dat["my"]==my] if i!=0])
    df["total_round"][i]= df["cr"][i]+ df["dr"][i] 
    df["total_entries"][i]= sum(dat["my"]==my)
    


# print("Round-Inwards-suspected Entries--->",sum([1 for i in dat.roundiw if i!=0]))
# print("Round-Outwards-suspected Entries--->",sum([1 for i in dat.roundow if i!=0]))

   
 return(dat,df)   
 



"""
fdf= pd.read_csv("df.csv")
dat=fdf[fdf.counter==51]
dat=dat.drop(["round","rt","Des","classification","cl_cl","gst"], axis=1)
#from sklearn.pipeline import Pipeline

#trns=  Pipeline([("clean",clean_transc(dat)),("pat",pattern(dat)),("round",round_entry(dat))])

#trns=  Pipeline([])
#needs class not def


list(dat)
dat= clean_transc(dat)
dat= round_entry(dat)
pat=pattern(dat)


fdf["iw_see"]=""
fdf["Description"]=[str(i).lower() for i in fdf["Description"]]
fdf["iw_see"]=["iw" if len(re.findall(r"iw",x))>0 else y for x,y in zip(fdf["Description"], fdf["iw_see"])]
fdf["iw_see"].value_counts()

#pattern---->r"\biw\b"

fdf["ow_see"]=""
fdf["Description"]=[str(i).lower() for i in fdf["Description"]]
fdf["ow_see"]=["ow" if len(re.findall(r"ow",x))>0 else y for x,y in zip(fdf["Description"], fdf["ow_see"])]
fdf["ow_see"].value_counts()
#pattern--> r"\bow\b"


###############################################################################
###############################################################################

"""



#import datetime
from sklearn import preprocessing
import matplotlib.pyplot as plt

def plot_months(dat):
  
  dat['DateTime'] = pd.to_datetime(dat['Date_new'])
  #dat.DateTime.iloc[1].day
  dat["day"]=dat.DateTime.apply(lambda x: x.day)
  dat["month"]=dat.DateTime.apply(lambda x: x.month)
  dat["year"]=dat.DateTime.apply(lambda x: x.year)

  dat=dat[["day","month","year", "Balance"]]


  df=pd.DataFrame()
  mw=pd.DataFrame({'day': range(1,32)})

  for i in set(dat["year"]):
    dat1=dat[dat.year==i]
    for j in set(dat["month"]):
      dat2= dat1[dat1.month==j]
      #df.sort_values('date').groupby('id').tail(1)
      dat3=dat2.groupby('day').tail(1)
      dat4=pd.merge(mw,dat3,on='day', how='left')
      dat4.year=i
      dat4.month=j
      dat4=dat4.fillna(0)
      #cant fill the 0 in bal now as we will need the values in initial days from the past month, if they are 0.    
      df=df.append(dat4)

#df["bal_cum"]=df.bal.cumsum()
  print("Balance data takes a lil time...")
  #df["new"]= 0
  for k in range(1,len(df)):
    #print("Balance data takes a lil time...")
    print('.', end='', flush=True)
    #df["new"]=df.Balance 
  #  df["new"].iloc[k] = df["Balance"].iloc[k] if df["Balance"].iloc[k]!=0 else df["Balance"].iloc[k]
    if df.Balance.iloc[k]==0:
      df.Balance.iloc[k]=df.Balance.iloc[k-1]
  
  """df["bul"]= [i if i!=0 else i.shift(-1) for i in dat.Balance[1:]]"""
    
#df["bal_cum"]= [i-j for i,j in zip(df["Credit"], df["Debit"])]

#df["bal_cum_norm2"]=preprocessing.scale(df.bal_cum)


  for year in set(df.year):
    #print(year)
    dfy=df[df.year==year]
    # plot data
    fig, ax = plt.subplots(figsize=(15,7))
    # use unstack()
    
    dfy.groupby(['day','month']).sum()['Balance'].unstack().plot(ax=ax) 
    fig.suptitle('Amount vs Days')
    plt.xlabel('Days')
    plt.ylabel('Amount')
  
    plt.savefig('Month_day_Balance_{}.png'.format(year))
  
  for year in set(df.year):
    #print(year)
    dfy=df[df.year==year]
    # plot data
    dfy.boxplot(column=["Balance"], by=["month"], figsize=(15,7))
    fig.suptitle('Balance Box vs Months')
    plt.xlabel('Months')
    plt.ylabel('Balance')
  
    plt.savefig('Month_day_Balance_{}_Box.png'.format(year))


#plot_months(fdf)

###############################################################################
###############################################################################
#Variance
def variance(dat):
  #dat.DateTime.iloc[1].day
  dat["day"]=dat.DateTime.apply(lambda x: x.day)
  dat["month"]=dat.DateTime.apply(lambda x: x.month)
  dat["year"]=dat.DateTime.apply(lambda x: x.year)

  dat=dat[["day","month","year", "Balance"]]

  #dat["cum"]= dat.Balance.cumsum()
  dfv=dat#[dat["cum"]!=0]
  for year in set(dfv.year):
    dfy=dfv[dfv.year==year]
    print(len(dfy))
    plt.plot(preprocessing.scale(dfy.groupby(['day','month']).sum()['Balance'].unstack().var()))
    plt.title('Balance Variance across Months')
    plt.ylabel('Variance')
    plt.xlabel('Months')
    plt.legend(list(set(dat.year)), loc='upper right')
    plt.savefig('Variance_Balance.png'.format(year))

#variance(dat)


#dat=fdf[fdf.counter==39]



######################################
##workspace
######################################


def workspace(inp):
 
 dat1= pd.read_excel(inp, sheet_name="All_Transaction")
 dat1= clean_transc(dat1)
 chngs={"number":"others",
       "INSUFFICIENT FUNDS":"return",
       "credit card": "creditcard",
       "nach":"nach/emi",
       "emi":"nach/emi",
       "charge":"charges",
       "o/w returnreturn":"o/wreturn",
       "Tax":"tax",
       "Transfer":"transfer",
       "IMPS":"imps",
       "sudhircharges": "charges",
       "Fund Transfer": "transfer",
       "ecs":"nach/emi",
       "third_party":"nach/emi",
       "ib":"transfer",
       "mmt": "cash",
       "sudhirreturn": "return" }

 dat1["classification"]= [chngs[i] if i in chngs else i for i in dat1["classification"]]

 # load json and create model
 json_file = open('model.json', 'r')
 loaded_model_json = json_file.read()
 json_file.close()

 loaded_model = model_from_json(loaded_model_json)
 # load weights into new model
 loaded_model.load_weights("model.h5")
 #print("Loaded model from disk")
 loaded_model.compile(loss="categorical_crossentropy", metrics=["acc"], optimizer= "adam")
 ###########################################################



 #load tokenizer

 with open('tokenizer.pickle', 'rb') as handle:
     tok = pickle.load(handle)
 #removing oov and changing it to the location of something irrelevant as "i" also because i is at 71 well within 2000
 tok.word_index["-OOV-"]=tok.word_index["i"]

 X=tok.texts_to_sequences(dat1["Des"])

 X=pad_sequences(X, maxlen=10)


 encoder = LabelEncoder()
 encoder.classes_ = np.load('classes.npy',allow_pickle=True)

 ###########now lets predict and check


 y_prob = loaded_model.predict(X) 
 y_classes = y_prob.argmax(axis=-1)

 dat1["predict"]= encoder.inverse_transform(y_classes)

 dat1["classification"]=[y if x=="Not_Tagged" else x for x,y in zip(dat1["classification"], dat1["predict"])]

 dat1["disbursement"]=[1 if y>z and x=="nach/emi"else 0 for x,y,z in zip(dat1["classification"], dat1["Credit"], dat1["Debit"]) ]
 dat1["classification"]=["disbursement" if y==1 else x for x,y in zip(dat1["classification"], dat1["disbursement"])]

 dat1["interest"]=[1 if y>z and x=="int_coll"else 0 for x,y,z in zip(dat1["classification"], dat1["Credit"], dat1["Debit"]) ]
 dat1["classification"]=["int_coll_credit" if y==1 else x for x,y in zip(dat1["classification"], dat1["interest"])]

 dat1=dat1.drop(labels=["cl_cl","Des_cl","predict","interest", "disbursement"], axis=1)
 
 return(dat1)






