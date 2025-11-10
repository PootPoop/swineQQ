"""
Chart Renderer for Swine Farm AI Assistant
Creates interactive Plotly visualizations based on chart specifications
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List


def render_chart(chart_spec: Dict[str, Any], data: List[Dict]) -> go.Figure:
    """
    Create a Plotly figure based on chart specification and data

    Args:
        chart_spec: Chart specification dict with type, axes, labels, etc.
        data: Query results as list of dicts

    Returns:
        Plotly Figure object
    """
    # Convert data to DataFrame for easier manipulation
    df = pd.DataFrame(data)

    chart_type = chart_spec["chart_type"]
    x_axis = chart_spec["x_axis"]
    y_axis = chart_spec["y_axis"]
    title = chart_spec["title"]
    x_label = chart_spec["x_label"]
    y_label = chart_spec["y_label"]
    color_by = chart_spec.get("color_by")
    height = chart_spec.get("height", 450)
    show_legend = chart_spec.get("show_legend", True)

    # Route to appropriate chart type renderer
    if chart_type == "line":
        fig = create_line_chart(df, x_axis, y_axis, title, x_label, y_label, color_by)

    elif chart_type == "multi_line":
        fig = create_multi_line_chart(df, x_axis, y_axis, title, x_label, y_label)

    elif chart_type == "bar":
        fig = create_bar_chart(df, x_axis, y_axis, title, x_label, y_label, color_by)

    elif chart_type == "grouped_bar":
        fig = create_grouped_bar_chart(df, x_axis, y_axis, title, x_label, y_label)

    elif chart_type == "scatter":
        fig = create_scatter_chart(df, x_axis, y_axis, title, x_label, y_label, color_by)

    elif chart_type == "heatmap":
        fig = create_heatmap(df, x_axis, y_axis, title, x_label, y_label)

    elif chart_type == "pie":
        fig = create_pie_chart(df, x_axis, y_axis, title)

    else:
        # Fallback to simple bar chart for categorical data
        fig = create_bar_chart(df, x_axis, y_axis, title, x_label, y_label, color_by)

    # Apply common styling
    fig.update_layout(
        height=height,
        showlegend=show_legend,
        hovermode="x unified",
        template="plotly_white",
        font=dict(size=12),
        title_font=dict(size=16, color="#2c3e50"),
        xaxis=dict(showgrid=True, gridcolor='#ecf0f1'),
        yaxis=dict(showgrid=True, gridcolor='#ecf0f1')
    )

    return fig


def create_line_chart(df, x_col, y_col, title, x_label, y_label, color_by=None):
    """Create a line chart"""
    if color_by and color_by in df.columns:
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_by,
            title=title,
            labels={x_col: x_label, y_col: y_label}
        )
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='lines+markers',
            name=y_label,
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
        )

    return fig


def create_multi_line_chart(df, x_col, y_cols, title, x_label, y_label):
    """Create a multi-line chart for comparing multiple metrics"""
    if isinstance(y_cols, str):
        y_cols = [y_cols]

    fig = go.Figure()

    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

    for idx, y_col in enumerate(y_cols):
        if y_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='lines+markers',
                name=y_col.replace('_', ' ').title(),
                line=dict(color=colors[idx % len(colors)], width=2.5),
                marker=dict(size=6)
            ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label
    )

    return fig


def create_bar_chart(df, x_col, y_col, title, x_label, y_label, color_by=None):
    """Create a bar chart"""
    # Sort by y value for better visualization
    df_sorted = df.sort_values(by=y_col, ascending=False)

    if color_by and color_by in df.columns:
        fig = px.bar(
            df_sorted,
            x=x_col,
            y=y_col,
            color=color_by,
            title=title,
            labels={x_col: x_label, y_col: y_label}
        )
    else:
        # Color bars based on value (gradient effect)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_sorted[x_col],
            y=df_sorted[y_col],
            name=y_label,
            marker=dict(
                color=df_sorted[y_col],
                colorscale='RdYlGn_r',  # Red-Yellow-Green reversed (high = red)
                showscale=True,
                colorbar=dict(title=y_label)
            )
        ))
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
        )

    return fig


def create_grouped_bar_chart(df, x_col, y_cols, title, x_label, y_label):
    """Create a grouped bar chart for multi-metric comparison"""
    if isinstance(y_cols, str):
        y_cols = [y_cols]

    fig = go.Figure()

    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

    for idx, y_col in enumerate(y_cols):
        if y_col in df.columns:
            fig.add_trace(go.Bar(
                x=df[x_col],
                y=df[y_col],
                name=y_col.replace('_', ' ').title(),
                marker_color=colors[idx % len(colors)]
            ))

    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        barmode='group'
    )

    return fig


def create_scatter_chart(df, x_col, y_col, title, x_label, y_label, color_by=None):
    """Create a scatter plot for correlation analysis"""
    if color_by and color_by in df.columns:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_by,
            title=title,
            labels={x_col: x_label, y_col: y_label},
            hover_data=df.columns.tolist()
        )
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='markers',
            marker=dict(
                size=10,
                color='#3498db',
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            text=df[color_by] if color_by and color_by in df.columns else None,
            hovertemplate=f'<b>{x_label}</b>: %{{x}}<br><b>{y_label}</b>: %{{y}}<extra></extra>'
        ))
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
        )

    # Add trendline if it's a correlation plot
    if len(df) > 2:
        try:
            from scipy import stats
            slope, intercept, r_value, p_value, std_err = stats.linregress(df[x_col].dropna(), df[y_col].dropna())
            line_x = [df[x_col].min(), df[x_col].max()]
            line_y = [slope * x + intercept for x in line_x]

            fig.add_trace(go.Scatter(
                x=line_x,
                y=line_y,
                mode='lines',
                name=f'Trend (R²={r_value**2:.3f})',
                line=dict(color='red', dash='dash', width=2)
            ))
        except:
            pass  # Skip trendline if calculation fails

    return fig


def create_heatmap(df, x_col, y_col, title, x_label, y_label):
    """Create a heatmap"""
    # Pivot data for heatmap if needed
    try:
        # Try to create a pivot table
        if len(df.columns) >= 3:
            z_col = [col for col in df.columns if col not in [x_col, y_col]][0]
            pivot_df = df.pivot(index=y_col, columns=x_col, values=z_col)

            fig = go.Figure(data=go.Heatmap(
                z=pivot_df.values,
                x=pivot_df.columns,
                y=pivot_df.index,
                colorscale='RdYlGn_r',
                hoverongaps=False
            ))
        else:
            # Fallback to simple heatmap
            fig = go.Figure(data=go.Heatmap(
                z=[df[y_col].tolist()],
                x=df[x_col].tolist(),
                y=['Values'],
                colorscale='RdYlGn_r'
            ))

        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label
        )

    except Exception as e:
        # Fallback to bar chart if heatmap fails
        print(f"Heatmap creation failed: {e}, using bar chart instead")
        fig = create_bar_chart(df, x_col, y_col, title, x_label, y_label, None)

    return fig


def create_pie_chart(df, labels_col, values_col, title):
    """Create a pie chart for categorical distribution"""
    # Sort by values for better visualization
    df_sorted = df.sort_values(by=values_col, ascending=False)

    # Limit to top 10 categories for readability
    if len(df_sorted) > 10:
        df_top = df_sorted.head(10)
        # Sum remaining into "Others"
        others_sum = df_sorted.tail(len(df_sorted) - 10)[values_col].sum()
        if others_sum > 0:
            others_row = pd.DataFrame({
                labels_col: ['Others'],
                values_col: [others_sum]
            })
            df_sorted = pd.concat([df_top, others_row], ignore_index=True)
        else:
            df_sorted = df_top

    fig = go.Figure(data=[go.Pie(
        labels=df_sorted[labels_col],
        values=df_sorted[values_col],
        hole=0.3,  # Donut chart style
        textposition='inside',
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percent}<extra></extra>',
        marker=dict(
            colors=px.colors.qualitative.Set3,
            line=dict(color='white', width=2)
        )
    )])

    fig.update_layout(
        title=title,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )

    return fig


def add_threshold_lines(fig, y_thresholds: Dict[str, float]):
    """
    Add horizontal threshold lines to chart (e.g., critical mortality level)

    Args:
        fig: Plotly figure
        y_thresholds: Dict of {label: value} for threshold lines

    Returns:
        Modified figure
    """
    colors = {'critical': 'red', 'warning': 'orange', 'good': 'green'}

    for label, value in y_thresholds.items():
        color = colors.get(label.lower(), 'gray')
        fig.add_hline(
            y=value,
            line_dash="dash",
            line_color=color,
            annotation_text=label,
            annotation_position="right"
        )

    return fig
