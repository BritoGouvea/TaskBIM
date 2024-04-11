import streamlit as st
from pandas import DataFrame
from classes.primavera_xml import Plan, Activity, ActivityCodeType

st.title('Primavera')

if 'xml' not in st.session_state:
    st.session_state['xml'] = None

try:
    plan: Plan = list(st.session_state['xml'].values())[0]

    activity_code_types = [ActivityCodeType.Name for ActivityCodeType in list(plan.ActivityCodeTypes.values())]

    def activity_row(activity: Activity, activity_code_types) -> dict:
        activity_dict = {"Id": activity.Id, "Name": activity.Name}
        for activity_code_type in activity_code_types:
            if activity_code_type in activity.ActivityCodes:
                activity_dict.update({activity_code_type: activity.ActivityCodes[activity_code_type]})
            else:
                activity_dict.update({activity_code_type: None})
        return activity_dict

    rows = [ activity_row(activity, activity_code_types) for activity in plan.Activities ]


    def activity_code_type_column(activity_code_type: ActivityCodeType):
            options = [ activity_code_type.Description for activity_code_type in activity_code_type.ActivityCodes ]
            options.sort()
            return st.column_config.SelectboxColumn(activity_code_type.Name, options=options)

    activity_code_type_columns = { activity_code_type.Name: activity_code_type_column(activity_code_type)
                                  for activity_code_type in plan.ActivityCodeTypes.values() }

    column_config = {
        'Id': st.column_config.TextColumn(
            "Id",
            disabled=True
        ),
        'Name': st.column_config.TextColumn(
            "Name",
            disabled=True
        )
    }

    column_config.update(activity_code_type_columns)

    dataframe = DataFrame(rows)

    st.data_editor(dataframe, use_container_width=True, height=700, column_config=column_config)

except:
    st.warning("Necessário carregar o planejamento em XML", icon="⚠️")