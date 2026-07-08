import plotly.graph_objects as go

def cloud_gauge(value):

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text":"Average Cloud Cover"},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"thickness":0.3},
                "steps":[
                    {"range":[0,30]},
                    {"range":[30,70]},
                    {"range":[70,100]}
                ]
            }
        )
    )

    return fig