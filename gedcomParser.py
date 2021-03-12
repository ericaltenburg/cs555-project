#Sarah Wiessler

from prettytable import PrettyTable
from datetime import *
from dateutil.parser import parse
from pymongo import MongoClient
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

f = open('family.ged', 'r')
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

#US01 date before current date method - sw
def before_current_date(date_args, curr_name, curr_id, prev_tag):
    if datetime.date(parse(date_args)) > today:
        print("Error US01: "+prev_tag+" date of "+curr_name+"("+curr_id+") occurs before the current date.")
        #returning for unit testing 
        return str("Error US01: "+prev_tag+" date of "+curr_name+"("+curr_id+") occurs before the current date.")
    else:
        return
#US02 birth of individual before marriage of individual
def marriage_before_birth(marr_date, birth_date, curr_name, curr_id):
    if datetime.date(parse(marr_date)) <  datetime.date(parse(birth_date)):
        print("Error US02: Marriage date of "+curr_name+"("+curr_id+") occurs before their birth date.")
        #returning for unit testing 
        return str("Error US02: Marriage date of "+curr_name+"("+curr_id+") occurs before their birth date.")
    else:
        return
#US03 birth before death of individual - mm
def death_before_birth(death_date, birth_date, curr_name, curr_id):
    if datetime.date(parse(death_date)) < datetime.date(parse(birth_date)):
        print("Error US03: Death date of "+curr_name+"("+curr_id+") occurs before their birth date.")
        #returning for unit testing 
        return "Error US03: Death date of "+curr_name+"("+curr_id+") occurs before their birth date."
    else:
        return
    
#parsing file
for line in Lines:
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
            person_list[person_count-1]["Birthday"] = arguments
            person_list[person_count-1]["Age"] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            #us01
            before_current_date(arguments, person_list[person_count-1]["Name"], person_list[person_count-1]["ID"].strip(), "Birth")
            birt_last = False
            continue
        if(tag == "DATE" and deat_next == True):
            person_list[person_count-1]["Alive"] = False
            person_list[person_count-1]["Death"] = arguments
            death = parse(arguments)
            person_list[person_count-1]["Age"] = (death.year - born.year - ((death.month, death.day) < (born.month, born.day)))
            #us01
            before_current_date(arguments, person_list[person_count-1]["Name"], person_list[person_count-1]["ID"].strip(), "Death")
            deat_next = False
            #us03
            for p_dict in person_list:
                if person_list[person_count-1]["Age"] < 0:
                    death_before_birth(p_dict["Death"], p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip())
            continue
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

    #Child and Spouse Check & Family Table build
    #((tag == "TYPE" and arguments == "Ending") or (tag == "TRLR"))
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
            #adds children to person list
##            for p_dict in person_list:
##                if (p_dict["ID"] == family_list[family_count-1]["Husband ID"]):
##                    p_dict["Child"] = family_list[family_count-1]["Children"]
##                if (p_dict["ID"] == family_list[family_count-1]["Wife ID"]):
##                    p_dict["Child"] = family_list[family_count-1]["Children"]
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
                    marriage_before_birth(arguments, p_dict["Birthday"], p_dict["Name"], p_dict["ID"].strip())    
            #us01
            before_current_date(arguments, "Family", family_list[family_count-1]["ID"].strip(), "Marriage")
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
            before_current_date(arguments, "Family", family_list[family_count-1]["ID"].strip(), "Divorce")
            div_next = False
            continue

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
