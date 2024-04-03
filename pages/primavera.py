import streamlit as st
from pandas import DataFrame
from classes.primavera_xml import Plan, Activity

st.title('Primavera')

if 'xml' not in st.session_state:
    st.session_state['xml'] = None
    
plan = list(st.session_state['xml'].values())[0]

if plan:

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

    dataframe = DataFrame(rows)

    st.data_editor(dataframe, use_container_width=True, height=700)

else:
    st.warning("Necessário carregar o planejamento em XML", icon="⚠️")