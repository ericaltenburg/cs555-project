#Sarah Wiessler

from prettytable import PrettyTable
from datetime import *
import dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient
import math
import os
from dotenv import load_dotenv

load_dotenv()

# Load MONGOURI from .env and create db
MONGOURI = os.getenv('mongoURI')
client = MongoClient(port=27017)
db = client.gedcom

individuals = PrettyTable()
individuals.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]

families = PrettyTable()
families.field_names = ["ID", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children", "Married", "Divorced"]
family_field_names = ["ID", "Husband ID", "Husband Name", "Wife ID", "Wife Name", "Children", "Married", "Divorced"]

f = open('family2.ged', 'r')
Lines = f.readlines()

tags = ["INDI", "NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "FAM", "MARR",
       "HUSB", "WIFE", "CHIL", "DIV", "DATE", "HEAD", "TRLR", "NOTE"]

#variables that cant reset
indi_hit = False
person_count = 0
person_list = []
today = date.today()
deat_next = False
birt_last = False
family_list = []
family_count = 0
marr_next = False
div_next = False
marr_last = False
husb_next = False
wife_next = False
chil_next = False
fams_last = False
#US15
old_children_list = []


#US01 date before current date method - sw
def before_current_date(date_args, curr_name, curr_id, prev_tag, lineNum):
    if datetime.date(parse(date_args)) > today:
        print("Error US01: "+prev_tag+" date of "+curr_name+"("+curr_id+") occurs before the current date on line "+lineNum+".")
        #returning for unit testing 
        return str("Error US01: "+prev_tag+" date of "+curr_name+"("+curr_id+") occurs before the current date on line "+lineNum+".")
    else:
        return
    
#US02 birth of individual before marriage of individual
def marriage_before_birth(marr_date, birth_date, curr_name, curr_id, lineNum):
    if datetime.date(parse(marr_date)) <  datetime.date(parse(birth_date)):
        print("Error US02: Marriage date of "+curr_name+"("+curr_id+") occurs before their birth date on line "+lineNum+".")
        #returning for unit testing 
        return str("Error US02: Marriage date of "+curr_name+"("+curr_id+") occurs before their birth date on line "+lineNum+".")
    else:
        return
    
#US03 birth before death of individual - mm
def death_before_birth(death_date, birth_date, curr_name, curr_id, lineNum):
    if datetime.date(parse(death_date)) < datetime.date(parse(birth_date)):
        print("Error US03: Death date of "+curr_name+"("+curr_id+") occurs before their birth date on line "+lineNum+".")
        #returning for unit testing 
        return "Error US03: Death date of "+curr_name+"("+curr_id+") occurs before their birth date on line "+lineNum+"."
    else:
        return
    
#US04 marriage before divorce of spouses - mm
def divorce_before_marriage(div_date, marr_date, curr_name, curr_id, lineNum):
    if datetime.date(parse(div_date)) < datetime.date(parse(marr_date)):
        print("Error US04: Divorce date of "+curr_name+"("+curr_id+") occurs before their marriage date on line "+lineNum+".")
        #returning for unit testing 
        return "Error US04: Divorce date of "+curr_name+"("+curr_id+") occurs before their marriage date on line "+lineNum+"."
    else:
        return
    
#US05 Marriage should occur before death of either spouse - cs
def death_before_marriage(death_date, marr_date, curr_name, curr_id, lineNum):
    if datetime.date(parse(death_date)) < datetime.date(parse(marr_date)):
        print("Error US05: Death date of " + curr_name + "(" + curr_id + ") occurs before their marriage date on line " + lineNum + ".")
        #returning for unit testing 
        return "Error US05: Death date of " + curr_name + "(" + curr_id + ") occurs before their marriage date on line " + lineNum + "."
    else:
        return
    
#US06 Divorce can only occur before death of both spouses - cs
def death_before_divorce(death_date, div_date, curr_name, curr_id, lineNum):
    if datetime.date(parse(death_date)) < datetime.date(parse(div_date)):
        print("Error US06: Death date of " + curr_name + "(" + curr_id + ") occurs before their divorce date on line " + lineNum + ".")
        #returning for unit testing 
        return "Error US06: Death date of " + curr_name + "(" + curr_id + ") occurs before their divorce date on line " + lineNum + "."
    else:
        return
    
#US07 Less than 150 years old
def greater_than_150(curr_age,curr_name, curr_id, lineNum):
    if int(curr_age) >= 150:
        error_str = "Error US07: Age of " +curr_name+"("+curr_id+") is not less than 150 on line "+lineNum+"."
        print(error_str)
        return error_str
    else:
        return

#US08 Birth before marriage of parents
def birth_before_marriage(birth_date, marr_date, div_date, curr_name, curr_id, fam_id, lineNum):
    if datetime.date(parse(birth_date)) < datetime.date(parse(marr_date)):
        anom_str = "Anomaly US08: Birth date of " +curr_name+"("+curr_id+") occurs before the marriage date of their parents in Family " + fam_id + " on line "+lineNum+"."
        print(anom_str)
        return anom_str
    elif div_date != "N/A" and datetime.date(parse(birth_date)) > (datetime.date(parse(div_date))+relativedelta(months=+9)):
        anom_str = "Anomaly US08: Birth date of " +curr_name+"("+curr_id+") occurs after 9 months from the divorce date of their parents in Family " + fam_id + " on line "+lineNum+"."
        print(anom_str)
        return anom_str
    else:
        return
    
#US09 Birth before death of parents
def birth_before_parents_death(child_birth_date, child_name, child_id, parent_death, is_mother, lineNum):
    if is_mother:
        if datetime.date(parse(child_birth_date)) > datetime.date(parse(parent_death)):
            error_str = "Error US09: Birth of " +child_name+"("+child_id+") is after the death of their mother on line "+lineNum+"."
            print(error_str)
            return error_str
    else:
        nine_month = dateutil.relativedelta.relativedelta(months=9)
        if datetime.date(parse(child_birth_date)) > datetime.date(parse(parent_death)-nine_month):
            error_str = "Error US09: Birth of " +child_name+"("+child_id+") is after 9 months after the death of their father on line "+lineNum+"."
            print(error_str)
            return error_str
    return;

#US10 Marriage after 14
def marriage_after_14(curr_id, curr_name, marr_date, birt_date, lineNum):
    time = datetime.date(parse(marr_date)) - datetime.date(parse(birt_date))
    yearsDifference = math.floor(time.total_seconds()/31536000)
    if yearsDifference < 14:
        error_str = "Error US10: Birth of " +curr_name+"("+curr_id+") is less than 14 years before their marriage date on line "+lineNum+"."
        print(error_str)
        return error_str
    
#US11 No Bigamy
def no_bigamy(marr_date1, marr_date2, div_date1, curr_name, curr_id, lineNum):
    if div_date1 == 'N/A' and datetime.date(parse(marr_date1)) < datetime.date(parse(marr_date2)): # 1st marriage and 2nd marriage going on at same time
        anom_str = "Anomaly US11: Marriage of " +curr_name+"("+curr_id+") occurred during another marriage on line "+lineNum+" (there is bigamy)."
        print(anom_str)
        return anom_str
    elif datetime.date(parse(marr_date2)) < datetime.date(parse(div_date1)): # 2nd marriage happened before the 1st marriage's divorce
        anom_str = "Anomaly US11: Marriage of " +curr_name+"("+curr_id+") occurred during another marriage on line "+lineNum+" (there is bigamy)."
        print(anom_str)
        return anom_str
    else:
        return

#US12 Parent not too old
def parent_too_old(cbirth, pbirth, p_name, curr_id, gender, lineNum):
    time = datetime.date(parse(cbirth)) - datetime.date(parse(pbirth))
    yearsDifference = math.floor(time.total_seconds()/31536000) #seconds in a year = 365 days
    if gender == 'F' and yearsDifference > 60:
        anom_str = "Anomaly US12: " +p_name+"("+curr_id+") is a mother who is "+str(yearsDifference)+" (more than 60) years older than her child on line "+lineNum+"."
        return anom_str
    elif gender == 'M' and yearsDifference > 80:
        anom_str = "Anomaly US12: " +p_name+"("+curr_id+") is a father who is "+str(yearsDifference)+" (more than 80) years older than his child on line "+lineNum+"."
        return anom_str
    else:
        return

#US15 Fewer than 15 siblings in a family (max of 15 children)
def more_than_15_siblings(sib_count, fam_id, lineNum):
    if (sib_count > 15):
        error_str = "Error US15: Family (" +fam_id+ ") has more than 15 siblings on line "+lineNum+"."
        print(error_str)
        return error_str
    else:
        return
    
#US16 Males in family must have same name as father
def different_last_names(father_name, p_name, curr_id, lineNum):
    if (father_name != p_name):
        error_str = "Error US16: "+p_name+" ("+curr_id+") does not have the same name as their father ("+father_name+") on line "+lineNum+"."
        print(error_str)
        return error_str
    else:
        return

    
#parsing file
for count, line in enumerate(Lines):
    #initializing line variables
    split = line.split()
    level = split[0]
    start = 2
    end = len(split)
    tag = split[1]
    arguments = ""

    #Checking INDI and FAM exceptions
    if ( len(split) == 3 and (split[2] == "INDI" or split[2] == "FAM") ):
        validOut = 'Y'
        start = 1
        end = end-1
        tag = split[2]
    #Checking name and date exceptions
    if( tag == "NAME" and level == "2" ):
        validOut = 'N'
    elif( tag == "DATE" and level == "1" ):
        validOut = 'N'
    #tag check
    if ( tag in tags ):
        validOut = 'Y'
    else:
        validOut = 'N'
    #Appending arguments
    for x in split[start:end]:
        arguments +=(x + " ")

    #Begin individual
    if( tag == "INDI" ):
        indi_hit = True
        #count for dictionary index
        person_count += 1
        #begin dictionary for individual
        person_list.append({"ID":arguments})
        #jump back to first loop
        continue
    #checking still in individual tags
    if( indi_hit == True ):
        #Appending to individual dictionary - Checks
        #Name check
        if(tag == "NAME"):
            person_list[person_count-1]["Name"] = arguments
            continue
        if(tag == "SEX"):
            person_list[person_count-1]["Gender"] = arguments
            continue
        #Alive and Age Check
        if(tag == "BIRT"):
            birt_last = True
            continue
        if(tag == "DATE" and birt_last == True):
            deat_next = True
            born = parse(arguments) 
            person_list[person_count-1] ["Birthday"] = arguments
            person_list[person_count-1]["Age"] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            #us01
            before_current_date(arguments, person_list[person_count-1]["Name"], person_list[person_count-1]["ID"].strip(), "Birth", str(count+1))
            #us07
            greater_than_150(person_list[person_count-1]["Age"], person_list[person_count-1]["Name"], person_list[person_count-1]["ID"].strip(), str(count+1))
            birt_last = False
            continue
        if(tag == "DATE" and deat_next == True):
            person_list[person_count-1]["Alive"] = False
            person_list[person_count-1]["Death"] = arguments
            death = parse(arguments)
            person_list[person_count-1]["Age"] = (death.year - born.year - ((death.month, death.day) < (born.month, born.day)))
            #us01
            before_current_date(arguments, person_list[person_count-1]["Name"], person_list[person_count-1]["ID"].strip(), "Death", str(count+1))
            deat_next = False
            #us03
            for p_dict in person_list:
                if p_dict["Age"] < 0:
                    #fixing n/a bug. 3.16
                    if(p_dict["Death"] != "N/A"):
                        death_before_birth(p_dict["Death"], p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip(), str(count+1))
        #up to death of individual
        if( tag == "FAMC" or tag == "FAMS"):
            if(deat_next == True):
                person_list[person_count-1]["Alive"] = True
                person_list[person_count-1]["Death"] = "N/A"
                deat_next = False
        #adding child and spouse
            if(tag == "FAMS"):
                person_list[person_count-1]["Spouse"] = arguments
                fams_last = True
                continue
            if(tag == "FAMC"):
                if(not fams_last):
                    person_list[person_count-1]["Spouse"] = "N/A"
                    person_list[person_count-1]["Child"] = arguments
                else:
                    person_list[person_count-1]["Child"] = arguments
                    fams_last = False
            #finish individual
            indi_hit = False
            continue

    #US15
    if (family_count > 0 and "Children" in family_list[family_count-1]):
        if (tag == "TRLR"):
            more_than_15_siblings(len(old_children_list), family_list[family_count-1]["ID"].strip(), str(count+1))
        if (len(old_children_list) == 0):
            old_children_list = family_list[family_count-1]["Children"].split()

        if (family_list[family_count-1]["Children"].split()[0] != old_children_list[0]):
            more_than_15_siblings(len(old_children_list), family_list[family_count-1]["ID"].strip(), str(count+1))

            old_children_list = family_list[family_count-1]["Children"].split()
        else:
            old_children_list = family_list[family_count-1]["Children"].split()

    

    #Child and Spouse Check & Family Table build
    if(indi_hit == False and person_list):
        #adding new family row
        if(tag == "FAM"):
            family_list.append({"ID":arguments})
            family_count+=1
            husb_next = True
            continue
        #husband and wife check
        if(husb_next == True and tag != "HUSB"):
            husb_next = False
            wife_next = True
            family_list[family_count-1]["Husband ID"] = "N/A"
            family_list[family_count-1]["Husband Name"] = "N/A"
        if(tag == "HUSB"):
            husb_next = False
            wife_next = True
            family_list[family_count-1]["Husband ID"] = arguments
            family_list[family_count-1]["Husband Name"] = next((sub for sub in person_list if sub['ID'] == arguments))["Name"]
            continue
        if(wife_next == True  and tag!= "WIFE"):
            wife_next = False
            chil_next = True
            family_list[family_count-1]["Wife ID"] = "N/A"
            family_list[family_count-1]["Wife Name"] = "N/A"
        if(tag == "WIFE"):
            wife_next = False
            chil_next = True
            family_list[family_count-1]["Wife ID"] = arguments
            family_list[family_count-1]["Wife Name"] = next((sub for sub in person_list if sub['ID'] == arguments))["Name"]
            continue
        #child check, will continue appending until child tag over
        if(chil_next == True and tag != "CHIL"):
            chil_next = False
            marr_next = True
            family_list[family_count-1]["Children"] = "N/A"
        if(tag == "CHIL"):
            chil_next = False
            marr_next = True
            if "Children" in family_list[family_count-1]:
                (family_list[family_count-1]["Children"]) += (arguments)
            else:
                family_list[family_count-1]["Children"] = arguments
           
            #US16
            for p_dict in person_list:
                if (p_dict["ID"] == arguments and p_dict["Gender"] == "M "):
                    father_name = family_list[family_count-1]["Husband Name"].split()[1][1:-1]
                    indiv_name = p_dict["Name"].split()[1][1:-1]
                    different_last_names(father_name, indiv_name, p_dict["ID"].strip(), str(count+1))
            continue
        #married and divorced check
        #wait for date arguments
        if(marr_next == True and (tag != "MARR" and tag!="DATE")):
            family_list[family_count-1]["Married"] = "N/A"
            marr_next = False
            div_next = True
        if(marr_next == True and tag == "MARR"):
            continue
        if(marr_next == True and tag == "DATE"):
            family_list[family_count-1]["Married"] = arguments
            #us02
            for p_dict in person_list:
                if (p_dict["ID"] == family_list[family_count-1]["Husband ID"] or p_dict["ID"] == family_list[family_count-1]["Wife ID"]):
                    marriage_before_birth(arguments, p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip(), str(count+1))
                    #us10
                    marriage_after_14(p_dict["ID"].strip(), p_dict["Name"], arguments, p_dict["Birthday"], str(count+1))
            #us01
            before_current_date(arguments, "Family", family_list[family_count-1]["ID"].strip(), "Marriage", str(count+1))
            marr_next = False
            div_next = True
            continue
        if(div_next == True and (tag != "DIV" and tag != "DATE" and tag!="PLAC")):
            family_list[family_count-1]["Divorced"] = "N/A"
            div_next = False
        if(div_next == True and tag == "DIV"):
            continue
        if(div_next == True and tag == "PLAC"):
            continue
        if(div_next == True and tag == "DATE"):
            family_list[family_count-1]["Divorced"] = arguments
            #us01
            before_current_date(arguments, "Family", family_list[family_count-1]["ID"].strip(), "Divorce", str(count+1))
            div_next = False
            #us04
            for p_dict in person_list:
                if (p_dict["ID"] == family_list[family_count-1]["Husband ID"] or p_dict["ID"] == family_list[family_count-1]["Wife ID"]):
                    divorce_before_marriage(family_list[family_count-1]["Divorced"], family_list[family_count-1]["Married"], p_dict["Name"], p_dict["ID"].strip(), str(count+1))
                    #us05
                    death_before_marriage(p_dict["Death"], family_list[family_count-1]["Married"], p_dict["Name"], p_dict["ID"].strip(), str(count+1))
                    #us06
                    death_before_divorce(p_dict["Death"], family_list[family_count-1]["Married"], p_dict["Name"], p_dict["ID"].strip(), str(count+1))
            continue
        #us09
        wife_death = "N/A"
        husb_death = "N/A"
        for p_dict in person_list:
            if p_dict["ID"].strip() == family_list[family_count-1]["Wife ID"].strip():
                wife_death = p_dict["Death"]
            elif p_dict["ID"].strip() == family_list[family_count-1]["Husband ID"].strip():
                husb_death = p_dict["Death"]
        #US08
        children_list_split = family_list[family_count-1]["Children"].split()
        for child in children_list_split:
            for p_dict in person_list:
                if p_dict["ID"].strip() == child:
                    birth_before_marriage(p_dict["Birthday"], family_list[family_count-1]["Married"], family_list[family_count-1]["Divorced"], p_dict["Name"], p_dict["ID"].strip(), family_list[family_count-1]["ID"].strip(), str(count+1))
                    #US09
                    if(wife_death != "N/A"):
                        birth_before_parents_death(p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip(), wife_death, True, str(count+1))
                    if(husb_death != "N/A"):
                        birth_before_parents_death(p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip(), husb_death, False, str(count+1))


        #US11

        # #US12
        # husband = family_list[family_count-1]["Husband ID"]
        # children = family_list[family_count-1]["Children"].split()
        # for c in children:
        #     childName = ""
        #     husbName = ""
        #     cbirth = ""
        #     pbirth = ""
        #     for p_dict in person_list:
        #         if p_dict["ID"].strip() == c:
        #             childName = p_dict["Name"]
        #             cbirth = p_dict["Birthday"]
        #             print(childName)
        #             print(cbirth)
        #         if p_dict["ID"].strip() == husband:
        #             husbName = p_dict["Name"]
        #             pbirth = p_dict["Birthday"]
        #     parent_too_old(cbirth, pbirth, husbName, husband, "M", str(count+1)) GIVES ERROR ON STRING NOT BEING ABLE TO BE PARSED




#adding individuals in the end
for indiv_dict in person_list:
     #Fills in child column if not complete
    if("Spouse" not in indiv_dict):
       indiv_dict["Spouse"] = "N/A"
    if("Child" not in indiv_dict):
       indiv_dict["Child"] = "N/A"
    individuals.add_row(indiv_dict.values())
    # Add to collection for individuals
    db.individuals.insert_one(indiv_dict)
print("Done adding individuals to \'individuals\' collection.")
#adding families in the end
for fam_dict in family_list:
    #Fills in last family if not complete
    while(len(fam_dict) != 8):
        key = family_field_names[len(fam_dict)]
        fam_dict[key] = "N/A"
    families.add_row(fam_dict.values())
    # Add to collection for families
    db.families.insert_one(fam_dict)
print("Done adding families to \'families\' collection.")
        
        
print("Individuals")
print(individuals)

print("Families")
print(families)
       
#close file
f.close()
