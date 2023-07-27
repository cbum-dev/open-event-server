from flask import url_for
from pentabarf.Conference import Conference
from pentabarf.Day import Day
from pentabarf.Event import Event
from pentabarf.Person import Person
from pentabarf.Room import Room
from sqlalchemy import Date, asc, func

from app.models import db
from app.models.event import Event as EventModel
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.settings import get_settings


def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f'{int(hours):02}:{int(minutes):02}'


class PentabarfExporter:
    def __init__(self):
        pass

    @staticmethod
    def export(event_id):
        """Takes an event id and returns the event in pentabarf XML format"""
        event = EventModel.query.get(event_id)
        diff = event.ends_at - event.starts_at

        conference = Conference(
            title=event.name,
            start=event.starts_at,
            end=event.ends_at,
            days=diff.days if diff.days > 0 else 1,
            day_change="00:00",
            timeslot_duration="00:15",
            venue=event.location_name,
        )
        dates = (
            db.session.query(
                func.date(Session.starts_at, type_=Date)
            )  # type_ needed for sqlite
            .filter_by(event_id=event_id)
            .filter_by(state='accepted')
            .filter(Session.deleted_at.is_(None))
            .order_by(asc(func.date(Session.starts_at)))
            .distinct()
            .all()
        )

        for date in dates:
            date = date[0]

            if date is None:
                continue  # Cannot continue if date is missing

            day = Day(date=date)
            microlocation_ids = list(
                db.session.query(Session.microlocation_id)
                .filter(func.date(Session.starts_at) == date)
                .filter_by(state='accepted')
                .filter(Session.deleted_at.is_(None))
                .order_by(asc(Session.microlocation_id))
                .distinct()
            )

            for microlocation_tuple in microlocation_ids:
                microlocation_id = microlocation_tuple[0]
                if microlocation_id:
                    microlocation = Microlocation.query.get(microlocation_id)
                    sessions = (
                        Session.query.filter_by(microlocation_id=microlocation_id)
                        .filter(func.date(Session.starts_at) == date)
                        .filter_by(state='accepted')
                        .filter(Session.deleted_at.is_(None))
                        .order_by(asc(Session.starts_at))
                        .all()
                    )

                    room = Room(name=microlocation.name)
                    for session in sessions:
                        if session.ends_at is None or session.starts_at is None:
                            duration = ""
                        else:
                            duration = format_timedelta(
                                session.ends_at - session.starts_at
                            )
                        session_event = Event(
                            id=session.id,
                            date=session.starts_at,
                            start=session.starts_at.strftime('%H:%M'),
                            duration=duration,
                            track=session.track.name,
                            abstract=session.short_abstract,
                            title=session.title,
                            type='Talk',
                            description=session.long_abstract,
                            conf_url=url_for(
                                'v1.event_list', identifier=event.identifier
                            ),
                            full_conf_url=url_for(
                                'v1.event_list',
                                identifier=event.identifier,
                                _external=True,
                            ),
                            released="True" if event.schedule_published_on else "False",
                        )

                        for speaker in session.speakers:
                            person = Person(id=speaker.id, name=speaker.name)
                            session_event.add_person(person)

                        room.add_event(session_event)
                    day.add_room(room)
            conference.add_day(day)

        return conference.generate("Generated by " + get_settings()['app_name'])
