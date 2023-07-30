import db.database as database

from sqlalchemy import Table
from sqlalchemy.orm import Session, sessionmaker

from fastapi import Depends, Body, FastAPI
from fastapi.responses import JSONResponse, FileResponse

SessionLocal = sessionmaker(autoflush=False, bind=database.engine)

app = FastAPI()

# определяем зависимость
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_total(table_class: type[Table], db: Session = Depends(get_db)) -> int:
    return db.query(table_class).count()

@app.get("/")
def main():
    print("Hello, boi!!!")

@app.get("/feed")
def get_posts(db: Session = Depends(get_db)):
    total = get_total(database.Lenta, db)
    return db.query(database.Lenta).where(database.Lenta.post_id.between(total-10, total))

@app.get("/feed")
def get_new_posts(last_id, db: Session = Depends(get_db)):
    db.query(database.Lenta).where(database.Lenta.post_id.between(last_id-10, last_id))

@app.post("/feed")
def create_new_post(data = Body(), db: Session = Depends(get_db)):
    post = database.Lenta(post_id = data["post_id"], author_id = data["author_id"], track_id = data["track_id"], annotation = data["annotation"])
    db.add()
    db.commit()
    db.refresh(post)
    return post

@app.get("/chat")
def get_dialogs(db: Session = Depends(get_db)):
    return db.query(database.Dialogs).all()

@app.post("/chat")
def create_new_chat(data = Body(), db: Session = Depends(get_db)):
    dialog = database.Dialogs(dialog_id = data["dialog_id"], user_one_id = data["user_one_id"], user_two_id = data["user_two_id"])
    db.add()
    db.commit()
    db.refresh(dialog)
    return dialog

@app.get("/chat/{dialog_id}")
def get_messages(dialog_id, db: Session = Depends(get_db)):
    chat = db.query(database.Messages).where(database.Messages.dialog_id.is_(dialog_id)).limit(10)
    return chat

@app.get("/chat/{dialog_id}")
def get_previous_messages(last_message_id, dialog_id, db: Session = Depends(get_db)):
    chat = db.query(database.Messages).where(database.Messages.dialog_id.is_(dialog_id).__and__(database.Messages.message_id < last_message_id)).limit(10)
    return chat

@app.post("/chat/{dialog_id}")
def create_new_message(data = Body(), db: Session = Depends(get_db)):
    message = database.Messages(message_id = data["message_id"], dialog_id = data["dialog_id"], sender_id = data["sender_id"], receiver_id = ["receiver_id"], send_date = ["send_date"], message_text = ["message_text"], attachment_id = ["attachment_id"])
    db.add()
    db.commit()
    db.refresh(message)
    return message 