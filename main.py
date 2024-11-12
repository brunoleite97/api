from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://testeagendador.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
def init_db():
    if not os.path.exists('appointments.db'):
        conn = sqlite3.connect('appointments.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE appointments
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             service TEXT NOT NULL,
             date TEXT NOT NULL,
             time TEXT NOT NULL)
        ''')
        conn.commit()
        conn.close()

init_db()

class Appointment(BaseModel):
    name: str
    service: str
    date: str
    time: str

@app.get("/appointments")
async def get_appointments():
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM appointments')
    appointments = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "service": row[2],
            "date": row[3],
            "time": row[4]
        }
        for row in appointments
    ]

@app.post("/appointments")
async def create_appointment(appointment: Appointment):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    try:
        c.execute(
            'INSERT INTO appointments (name, service, date, time) VALUES (?, ?, ?, ?)',
            (appointment.name, appointment.service, appointment.date, appointment.time)
        )
        conn.commit()
        appointment_id = c.lastrowid
        conn.close()
        
        return {
            "id": appointment_id,
            **appointment.dict()
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/appointments/filter")
async def filter_appointments(name: str = None, service: str = None, date: str = None):
    conn = sqlite3.connect('appointments.db')
    c = conn.cursor()
    
    query = 'SELECT * FROM appointments WHERE 1=1'
    params = []
    
    if name:
        query += ' AND name LIKE ?'
        params.append(f'%{name}%')
    if service:
        query += ' AND service LIKE ?'
        params.append(f'%{service}%')
    if date:
        query += ' AND date = ?'
        params.append(date)
    
    c.execute(query, params)
    appointments = c.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "name": row[1],
            "service": row[2],
            "date": row[3],
            "time": row[4]
        }
        for row in appointments
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)