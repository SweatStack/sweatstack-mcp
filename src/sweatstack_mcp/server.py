import os
from io import BytesIO
from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import sweatstack as ss
from mcp.server.fastmcp import FastMCP, Image
from dotenv import load_dotenv


load_dotenv()


assert "SWEATSTACK_API_KEY" in os.environ, "SWEATSTACK_API_KEY is not set. Set it in the .env file."


server = FastMCP("SweatStack MCP Server")


@server.tool()
async def get_activity_details(activity_id: str) -> ss.schemas.ActivityDetails:
    """Get the details for an activity from SweatStack."""
    return ss.get_activity_details(activity_id=activity_id)


@server.tool()
async def get_latest_activity_details(sport: ss.schemas.Sport | None = None) -> ss.schemas.ActivityDetails:
    """Get the latest activity details from SweatStack. If sport is provided, get the latest activity for that sport."""
    if sport is not None:
        return ss.get_latest_activity(sport=sport)
    else:
        return ss.get_latest_activity()


def make_activity_data_llm_friendly(data: pd.DataFrame) -> str:
    """Make the activity data llm friendly.
    1. Convert timestamp to local time and rename to "datetime"
    2. Add cumulative distance column calculated from duration times speed
    3. Remove duration column
    4. Sort columns by datetime, then other columns
    """
    # 1. Convert timestamp column to local time and rename to "datetime"
    data["datetime"] = pd.to_datetime(data.index).tz_localize(None)  # Remove timezone info to convert to local time
    data = data.reset_index(drop=True)  # Remove the original timestamp index

    # 2. Add cumulative distance column calculated from duration × speed
    if "duration" in data.columns and "speed" in data.columns:
        data["distance_increment"] = data["duration"].dt.total_seconds() * data["speed"]
        data["distance"] = data.groupby("activity_id")["distance_increment"].cumsum()
        data = data.drop("distance_increment", axis=1)

    # 3. Remove duration column
    data = data.drop("duration", axis=1)

    # 4. Sort columns by datetime, then other columns
    priority_columns = ["datetime"]
    existing_priority_columns = [col for col in priority_columns if col in data.columns]
    other_columns = [col for col in data.columns if col not in priority_columns]
    data = data[existing_priority_columns + sorted(other_columns)]

    return data.to_csv(index=False)


def determine_adaptive_sampling_kwargs(activity_id: str) -> ss.Metric:
    activity = ss.get_activity(activity_id=activity_id)
    if activity.sport.is_sub_sport_of(ss.Sport.cycling):
        adaptive_sampling_on = ss.Metric.power
    else:
        if ss.Metric.power in activity.metrics:
            adaptive_sampling_on = ss.Metric.power
        else:
            adaptive_sampling_on = ss.Metric.speed
    
    extra_kwargs = {}
    
    if adaptive_sampling_on in activity.metrics:
        extra_kwargs["adaptive_sampling_on"] = adaptive_sampling_on.value
    
    return extra_kwargs


@server.tool()
async def get_activity_data(activity_id: str) -> str:
    """
    Get the timeseries data for an activity from SweatStack.
    By default, data is downsampled (adaptive_sampling=True) to reduce the size of the data.
    Returns a csv string.
    """
    extra_kwargs = {}
    extra_kwargs.update(determine_adaptive_sampling_kwargs(activity_id))
    
    data = ss.get_activity_data(activity_id=activity_id, **extra_kwargs)

    return make_activity_data_llm_friendly(data)


@server.tool()
async def get_latest_activity_data(sport: ss.schemas.Sport | None = None) -> str:
    """
    Get the timeseries data for the latest activity from SweatStack.
    By default, data is downsampled (adaptive_sampling=True) to reduce the size of the data.
    Returns a csv string.
    """
    latest_activity = ss.get_latest_activity(sport)

    extra_kwargs = {}
    extra_kwargs.update(determine_adaptive_sampling_kwargs(latest_activity.id))

    data = ss.get_latest_activity_data(sport=sport, **extra_kwargs)

    return make_activity_data_llm_friendly(data)


@server.tool()
async def get_activity_mean_max_values(
    activity_id: str,
    metric: Literal[ss.Metric.power.value, ss.Metric.speed.value],
    ) -> str:
    """
    Get the mean and max values for an activity from SweatStack.
    Mean max describe the maximum average value for each possible duration for the specified.
    It is different than the timeseries data and should not be used to calculate mean values.
    Only power and speed metrics are supported.
    Returns a csv string.
    """
    data = ss.get_activity_data(activity_id=activity_id)
    return data.groupby("activity_id")[metric].agg(["mean", "max"]).to_csv(index=False)


@server.tool()
async def get_activity_plot(activity_id: str, metric: str | ss.Metric) -> Image | str:
    """Get a plot of the timeseries data for an activity for a specific metric."""
    data = ss.get_activity_data(activity_id)
    if isinstance(metric, str):
        metric = ss.Metric(metric)

    if metric.value not in data.columns:
        return f"Metric {metric} not found in this activity. Try a different metric or activity."

    plt.plot(
        (data.index - data.index.min()).total_seconds() / 60,
        data[metric.value],
        color="black",
    )
    plt.xlabel("time [minutes]")
    plt.ylabel(metric.value)
    plt.title(f"Activity {activity_id}")

    image_data = BytesIO()
    plt.savefig(image_data, format="JPEG")
    image_data.seek(0)

    return Image(data=image_data.getvalue(), format="jpeg")


@server.tool()
async def get_latest_activity_plot(metric: str | ss.Metric, sport: ss.schemas.Sport | None = None) -> Image:
    """Get a plot of the timeseries data for the latest activity for a specific metric."""
    latest_activity = ss.get_latest_activity(sport=sport)

    return await get_activity_plot(latest_activity.id, metric)