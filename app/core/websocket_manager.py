from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.cam_connections: List[WebSocket] = [] 
        self.app_connections: List[WebSocket] = []  

    async def connect_cam(self, websocket: WebSocket):
        await websocket.accept()
        self.cam_connections.append(websocket)
        print(f"CAM connected | Total CAM: {len(self.cam_connections)}")

    def disconnect_cam(self, websocket: WebSocket):
        if websocket in self.cam_connections:
            self.cam_connections.remove(websocket)
            print(f"CAM disconnected | Total CAM: {len(self.cam_connections)}")

    async def connect_app(self, websocket: WebSocket):
        await websocket.accept()
        self.app_connections.append(websocket)
        print(f"Flutter App connected | Total App: {len(self.app_connections)}")

    def disconnect_app(self, websocket: WebSocket):
        if websocket in self.app_connections:
            self.app_connections.remove(websocket)
            print(f"Flutter App disconnected | Total App: {len(self.app_connections)}")

    async def broadcast_to_app(self, message: dict):
        dead = []
        for connection in self.app_connections:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.disconnect_app(conn)

    async def broadcast_to_cam(self, message: dict):
        dead = []
        for connection in self.cam_connections:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        for conn in dead:
            self.disconnect_cam(conn)


# singleton
manager = ConnectionManager()