import pandas as pd

def make_ref_file(full_path="", name="", use_abstract=True, use_summary=True, use_translate=True):
    batch_queries = {'Year': {}, 'Office': {}, 'GEROS Rating': {}, 'Language': {}, 'Category': {}, 'Region': {}, "Budget":{}}#additionally to these standard fields, fields for enablers and change strategies are added in the script
    print(batch_queries.keys())

    #############################Convert the spreadsheet into a RIS file that can be loaded into SWIFT, so that docs can be tagged using the batch queries
    df = pd.read_csv(r'C:\Users\c1049033\PycharmProjects\swift_tags\eisi_clean_2025.csv', encoding='utf-8-sig').fillna('')#The spreadsheet where majority of data comes from

    print(df.shape)
    ####################################################Filter spreadsheet, if needed
    geros_not=['Fair']
    # years=[2020, 2022, 2019, 2018, 2021]

    df=df[~df['GEROSRating'].isin(geros_not)]
    # df=df[df['Year'].isin(years)]
    # df=df[df['Type']=='Evaluation']
    # df=df[df['Status']=='Completed']
    # print(df.shape)
    ##########################################################

    def split_furhter(my_inp):
        out_set=set()
        for val in my_inp:
            for v in val.split(";"):
                out_set.add(v.strip())
        return out_set

    lines = []
    all_tags=set()
    #####################################retrieve change strategies and enabler labels
    set_changestrat = set()
    [set_changestrat.add(va.strip()) for va in df['Change Strategy CLEAN'].unique() if len(va.strip())>0]

    [set_changestrat.add(va.strip()) for va in df['Additional Change Strategy (ies)'].unique() if len(va.strip()) > 0]

    set_changestrat=split_furhter(set_changestrat)

    set_enabler = set()
    [set_enabler.add(va.strip()) for va in df['Enabler CLEAN'].unique() if len(va.strip())>0]


    [set_enabler.add(va.strip()) for va in df['Additional Enabler (s)'].unique() if len(va.strip()) > 0]
    set_enabler = split_furhter(set_enabler)




    for i, row in df.iterrows():

            tags_to_add = []
            my_id="ID:"+str(row["Id"])
            tags_to_add.append(my_id)




            abstr = row["Description"].replace("  ", " ").replace("\n", " ")  # +' Keywords: '
            lines.append("TY  - JOUR\n")
            lines.append("T1  - {}\n".format(row["Title"].replace("  ", " ").replace("\n"," ")))  # annoying newlines in excel file make the RIS file look ugly :)

            year_val=row["Year"]
            try:
                year_val= int(year_val)
                lines.append("PY  - {}\n".format(year_val))
                batch_queries['Year'][year_val] = batch_queries['Year'].get(year_val, [])
                batch_queries['Year'][year_val].append(my_id)
                tags_to_add.append("year:{}".format(year_val))
            except:
                print("Unable to extract year from report {}".format(i))


            lines.append("ST  - {}\n".format(row['ContactPerson'].replace("  ", " ").replace("\n", " ")))
            lines.append("AU  - {}\n".format(row['ContactPerson'].replace("  ", " ").replace("\n", " ")))

            ###################CHange strategies
            cnts = []  # save
            kwds = []  # for additional concepts only to be added as keywords

            for a in set_changestrat:
                if a in row["Change Strategy CLEAN"]:
                    cnts.append(a)
                if a in row["Additional Change Strategy (ies)"]:
                    kwds.append(a)

            for cnt in cnts:
                cnt = cnt.strip()  # .replace(" ", "")
                lines.append("KW  - change_strategy_primary:{}\n".format(cnt))
                batch_queries['Change_primary'] = batch_queries.get('Change_primary', {})
                batch_queries['Change_primary'][cnt] = batch_queries['Change_primary'].get(cnt, [])
                batch_queries['Change_primary'][cnt].append(my_id)

            for cnt in kwds:
                cnt = cnt.strip()  # .replace(" ", "")
                lines.append("KW  - change_strategy_secondary:{}\n".format(cnt))
                batch_queries['Change_secondary'] = batch_queries.get('Change_secondary', {})
                batch_queries['Change_secondary'][cnt] = batch_queries['Change_secondary'].get(cnt, [])
                batch_queries['Change_secondary'][cnt].append(my_id)

            #############################Enablers clean
            cnts = []  # save
            kwds = []

            for a in set_enabler:
                if a in row["Enabler CLEAN"]:
                    cnts.append(a)
                if a in row["Additional Enabler (s)"]:
                    kwds.append(a)

            for cnt in cnts:
                cnt = cnt.strip()  # .replace(" ", "")
                lines.append("KW  - enabler_primary:{}\n".format(cnt))
                batch_queries['Enabler_primary'] = batch_queries.get('Enabler_primary', {})
                batch_queries['Enabler_primary'][cnt] = batch_queries['Enabler_primary'].get(cnt, [])
                batch_queries['Enabler_primary'][cnt].append(my_id)

            for cnt in kwds:
                cnt = cnt.strip()  # .replace(" ", "")
                lines.append("KW  - enabler_secondary:{}\n".format(cnt))
                batch_queries['Enabler_secondary'] = batch_queries.get('Enabler_secondary', {})
                batch_queries['Enabler_secondary'][cnt] = batch_queries['Enabler_secondary'].get(cnt, [])
                batch_queries['Enabler_secondary'][cnt].append(my_id)


            ################################Budget
            bud=row["ActualBudgetUNICEF"]
            try:
                bud=int(bud)
                clean_bud=""
                if bud<=50000:
                    clean_bud="<50k"
                elif bud <=100000:
                    clean_bud = "50to100k"
                elif bud <= 150000:
                    clean_bud = "100to150k"
                elif bud > 150000:
                    clean_bud = ">150k"

                if bud != '':
                    lines.append("KW  - budget:{}\n".format(clean_bud))
                    tags_to_add.append("budget:{}".format(clean_bud))
                    batch_queries['Budget'][clean_bud] = batch_queries['Budget'].get(clean_bud, [])
                    batch_queries['Budget'][clean_bud].append(my_id)
            except:
                print("Budget not assigned for : {}".format(row["ActualBudgetUNICEF"]))


            cnt = row['Office'].replace("\n", " ").replace("  ", " ")
            if cnt != '':
                lines.append("KW  - country:{}\n".format(cnt))
                tags_to_add.append("country:{}".format(cnt))
                lines.append("CY  - {}\n".format(cnt))
                lines.append("PP  - {}\n".format(cnt))

                batch_queries['Office'][cnt] = batch_queries['Office'].get(cnt, [])
                batch_queries['Office'][cnt].append(my_id)

            reg = row['Region'].replace("  ", " ").replace("\n", " ")
            if reg != '':
                lines.append("KW  - region:{}\n".format(reg))
                tags_to_add.append("region:{}".format(reg))
                batch_queries['Region'][reg] = batch_queries['Region'].get(reg, [])
                batch_queries['Region'][reg].append(my_id)

            ger = row['GEROSRating'].replace(" ", " ").replace("\n", "")
            if ger != '':
                lines.append("KW  - geros:{}\n".format(ger))
                tags_to_add.append("geros:{}".format(ger))
                batch_queries['GEROS Rating'][ger] = batch_queries['GEROS Rating'].get(ger, [])
                batch_queries['GEROS Rating'][ger].append(my_id)



            cnt = row['Language'].replace("  ", " ").replace("\n", " ")
            if cnt != '':
                lines.append("KW  - language:{}\n".format(cnt))
                tags_to_add.append("language:{}".format(cnt))
                batch_queries['Language'][cnt] = batch_queries['Language'].get(cnt, [])
                batch_queries['Language'][cnt].append(my_id)

            cnt = row['Category'].replace("  ", " ").replace("\n", " ")  # formerly Impact Evaluation?
            if cnt != '':
                lines.append("KW  - category:{}\n".format(cnt))
                tags_to_add.append("category:{}".format(cnt))
                batch_queries['Category'][cnt] = batch_queries['Category'].get(cnt, [])
                batch_queries['Category'][cnt].append(my_id)



            # cnt=row['Humanitarian?'].replace("  "," ").replace("\n"," ")
            # if cnt != '':
            #     lines.append("KW  - humanitarian:{}\n".format(cnt))
            #     abstr = '{} humanitarian:{} ;'.format(abstr, cnt)

            # cnt = row['Case study'].replace("  ", " ").replace("\n", " ")  # only for new data
            # if cnt != '':
            #     lines.append("KW  - case study:{}\n".format(cnt))
            #     abstr = '{} case study:{} ;'.format(abstr, cnt)
            #     batch_queries['Case study'][cnt] = batch_queries['Case study'].get(cnt, [])
            #     batch_queries['Case study'][cnt].append(row['ID#'])


            cnts=[]#save goals in a list
            areas=['Goal 1', 'Goal 2', 'Goal 3', 'Goal 4', 'Goal 5']
            for a in areas:
                if a in row["StrategicGoals"]:
                    cnts.append(a)

            for cnt in cnts:
                cnt=cnt.replace("Goal ", "GA").strip()
                lines.append("KW  - goal:{}\n".format(cnt))
                tags_to_add.append("goal:{}".format(cnt))
                batch_queries['goal']=batch_queries.get('goal', {})
                batch_queries['goal'][cnt] = batch_queries['goal'].get(cnt, [])
                batch_queries['goal'][cnt].append(my_id)

            cnts = []  # save SDG goals in a list
            areas = ['SDG 01', 'SDG 02', 'SDG 03', 'SDG 04', 'SDG 05', 'SDG 06', 'SDG 07', 'SDG 08', 'SDG 09',
                     'SDG 10','SDG 11', 'SDG 12', 'SDG 13', 'SDG 14', 'SDG 15', 'SDG 16', 'SDG 17']

            for a in areas:
                if a in row["SDGs"]:
                    cnts.append(a)

            for cnt in cnts:
                cnt = cnt.replace(" ", "").strip()
                lines.append("KW  - SDG:{}\n".format(cnt))
                tags_to_add.append("SDG:{}".format(cnt))
                batch_queries['SDG'] = batch_queries.get('SDG', {})
                batch_queries['SDG'][cnt] = batch_queries['SDG'].get(cnt, [])
                batch_queries['SDG'][cnt].append(my_id)






            #abstr = '{} ID:{} ;'.format(abstr, row['ID#'])
            lines.append("ID  - {}\n".format(my_id))
            lines.append("T2  - {}\n".format(my_id))

            abstr="{} Custom Coding: {}".format(abstr, "; ".join(tags_to_add))

            lines.append("AB  - {}\n".format(abstr))
            lines.append("UR  - https://www.unicef.org/evaluation/reports#/detail/{}\n".format(str(row["Id"]).strip()))
            lines.append("ER  - \n")
            lines.append("\n")
            [all_tags.add(t) for t in tags_to_add]#to record all tags in existence

    with open("{}_refs_tags.ris".format(df.shape[0]), "w", encoding='utf-8') as f:
        f.writelines(lines)
        print('Done')

    for k,v in batch_queries.items():
        print("TAG CATEGORY {} has the following codes: {}".format(k, ", ".join([str(x).replace(",","") for x in sorted(v.keys())])))

        for key, value in v.items():
            print("\nCode {} has {} evaluations:".format(key, len(value)))
            print(" OR ".join(value))
        print("---------\n")

    print("All tags:")
    [print(t) for t in sorted(all_tags) if 'ID:' not in t]

make_ref_file()
