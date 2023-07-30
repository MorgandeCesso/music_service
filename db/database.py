from typing import List
from datetime import datetime, time
from sqlalchemy import ForeignKey
from sqlalchemy import String, Boolean
from sqlalchemy import DateTime, Time
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, query
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Base(DeclarativeBase):
    pass

class User_type(Base):
    __tablename__ = "User_type"
    type_id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(15))
    user_ref: Mapped["User"] = relationship(back_populates="usertype_ref")

    def __repr__(self) -> str:
        return f"User_type(Type_ID={self.type_id!r}, Type_name={self.type_name!r})"

class User(Base):
    __tablename__ = "Users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(40))
    hashed_password: Mapped[str] = mapped_column(String)
    refresh_token: Mapped[str] = mapped_column(String)
    user_type: Mapped[List["User_type"]] = mapped_column(ForeignKey("User_type.type_id"))
    usertype_ref: Mapped["User_type"] = relationship(back_populates="user_ref")
    message_ref: Mapped["Messages"] = relationship(back_populates="user_ref")
    lenta_ref: Mapped["Lenta"] = relationship(back_populates="user_ref")
    dialogs_ref: Mapped["Dialogs"] = relationship(back_populates="user_ref")

    def __repr__(self) -> str:
        return f"Users(User_ID={self.user_id!r}, Nickname={self.nickname!r}, eMail={self.email!r}, Hashed_password={self.hashed_password!r})"
    
class Attachments_Message(Base):
    __tablename__ = "Attachments_Chat"
    attachment_id: Mapped[int] = mapped_column(primary_key=True)
    attachment_path: Mapped[str] = mapped_column(String)
    message_ref: Mapped["Messages"] = relationship(back_populates="attachments_message_ref")

    def __repr__(self) -> str:
        return f"Attachments_Chat(Attachment_ID={self.attachment_id!r}, Attachment_path={self.attachment_path!r})"
    

class Dialogs(Base):
    __tablename__ = "Dialogs"
    dialog_id: Mapped[int] = mapped_column(primary_key=True)
    user_one_id: Mapped[List["User"]] = mapped_column(ForeignKey("Users.user_id"))
    user_two_id: Mapped[List["User"]] = mapped_column(ForeignKey("Users.user_id"))
    user_ref: Mapped["User"] = relationship(back_populates="dialogs_ref")
    messages_ref: Mapped["Messages"] = relationship(back_populates="dialogs_ref")
    def __repr__(self) -> str:
        return f"Dialogs(Dialog_ID={self.dialog_id!r}, User_one_ID={self.user_one_id!r}, User_two_ID={self.user_two_id!r})"

class Messages(Base):
    __tablename__ = "Messages"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    dialog_id: Mapped[List["Dialogs"]] = mapped_column(ForeignKey("Dialogs.dialog_id"))
    sender_id: Mapped[List["User"]] = mapped_column(ForeignKey("Users.user_id"))
    receiver_id: Mapped[List["User"]] = mapped_column(ForeignKey("Users.user_id"))
    send_date: Mapped[datetime] = mapped_column(DateTime)
    message_text: Mapped[str] = mapped_column(String(500))
    attachment_id: Mapped[List["Attachments_Message"]] = mapped_column(ForeignKey("Attachments_Chat.attachment_id"))
    user_ref: Mapped["User"] = relationship(back_populates="message_ref")
    dialogs_ref: Mapped["Dialogs"] = relationship(back_populates="Messages_ref")
    attachments_message_ref: Mapped["Attachments_Message"] = relationship(back_populates="message_ref")

    def __repr__(self) -> str:
        return f"Chat(Message_ID={self.message_id!r}, Dialog_ID={self.dialog_id!r}, Sender_ID={self.sender_id!r}, Receiver_ID={self.receiver_id!r}, Send_date={self.send_date!r}, Message_text={self.message_text!r}, Attachment_ID={self.attachment_id!r})"

class Music(Base):
    __tablename__ = "Music"
    track_id: Mapped[int] = mapped_column(primary_key=True)
    track_name: Mapped[str] = mapped_column(String(30))
    track_author: Mapped[str] = mapped_column(String(30))
    track_lyrics: Mapped[str] = mapped_column(String)
    track_time: Mapped[time] = mapped_column(Time)
    for_sale: Mapped[bool] = mapped_column(Boolean)
    lenta_ref: Mapped["Lenta"] = relationship(back_populates="music_ref")
    attachments_music_ref: Mapped["Attachments_Music"] = relationship(back_populates="music_ref")

    def __repr__(self) -> str:
        return f"Music(Track_ID={self.track_id!r}, Track_name={self.track_name!r}, Track_author={self.track_author!r}, Track_lyrics={self.track_lyrics!r}, Track_time={self.track_time!r})"

class Lenta(Base):
    __tablename__ = "Lenta"
    post_id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[List["User"]] = mapped_column(ForeignKey("User.user_id"))
    track_id: Mapped[List["Music"]] = mapped_column(ForeignKey("Music.track_id"))
    annotation: Mapped[str] = mapped_column(String(250))
    music_ref: Mapped["Music"] = relationship(back_populates="lenta_ref")
    user_ref: Mapped["User"] = relationship(back_populates="lenta_ref")
    
    def __repr__(self) -> str:
        return f"Lenta(Post_ID={self.post_id!r}, Author_ID={self.author_id!r}, Track_ID={self.track_id!r}, Annotation={self.annotation!r})"

class Attachments_Music(Base):
    __tablename__ = "Attachments_Music"
    attachment_id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[List["Music"]] = mapped_column(ForeignKey("Music.track_id"))
    track_path: Mapped[str] = mapped_column(String)
    track_cover_path: Mapped[str] = mapped_column(String)
    music_ref: Mapped["Music"] = relationship(back_populates="attachments_music_ref")

    def __repr__(self) -> str:
        return f"Attachments_Music(Attachment_ID={self.attachment_id!r}, Track_path={self.track_path}, Track_cover_Path={self.track_cover_path!r})"

def db_create():
    # Устанавливаем соединение с postgres
    connection = psycopg2.connect(user="postgres", password="Maximsid2003")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    # Создаем курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    sql_create_database = cursor.execute('create database summer_project')
    # Создаем базу данных
    # Закрываем соединение
    cursor.close()
    connection.close()

engine = create_engine("postgresql+psycopg2://postgres:Maximsid2003@localhost:5432/summer_project", echo=True)
