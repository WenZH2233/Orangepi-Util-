from typing import Optional
from .calendar.tools import (
    create_event as _create_event,
    get_events_by_date as _get_events_by_date,
    update_event as _update_event,
    delete_event as _delete_event,
    delete_events_batch as _delete_events_batch,
    get_categories as _get_categories,
    get_upcoming_events as _get_upcoming_events
)

async def create_event(title: str, start_time: str, end_time: Optional[str] = None, description: str = "", category: str = "默认", reminder_minutes: int = 15) -> str:
    """
    Create a calendar event.
    start_time and end_time should be in ISO format (e.g. '2023-10-27T10:00:00').
    """
    return await _create_event({
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "category": category,
        "reminder_minutes": reminder_minutes
    })

async def get_events_by_date(date_type: str = "today", category: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Get events by date.
    date_type: 'today', 'tomorrow', 'week', 'month', or 'custom' (requires start_date and end_date).
    """
    return await _get_events_by_date({
        "date_type": date_type,
        "category": category,
        "start_date": start_date,
        "end_date": end_date
    })

async def update_event(event_id: int, title: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None, reminder_minutes: Optional[int] = None) -> str:
    """
    Update an existing event.
    """
    args = {"event_id": event_id}
    if title: args["title"] = title
    if start_time: args["start_time"] = start_time
    if end_time: args["end_time"] = end_time
    if description: args["description"] = description
    if category: args["category"] = category
    if reminder_minutes is not None: args["reminder_minutes"] = reminder_minutes
    return await _update_event(args)

async def delete_event(event_id: int) -> str:
    """
    Delete an event by ID.
    """
    return await _delete_event({"event_id": event_id})

async def delete_events_batch(date_type: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, category: Optional[str] = None, delete_all: bool = False) -> str:
    """
    Batch delete events.
    """
    return await _delete_events_batch({
        "date_type": date_type,
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "delete_all": delete_all
    })

async def get_categories() -> str:
    """
    Get all event categories.
    """
    return await _get_categories({})

async def get_upcoming_events(hours: int = 24) -> str:
    """
    Get upcoming events within the specified hours (default 24).
    """
    return await _get_upcoming_events({"hours": hours})
