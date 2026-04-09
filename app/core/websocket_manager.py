import websocket
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.cam_connections: List[WebSocket] = []
        self.app_connections: List[WebSocket] = []

    async def connect_cam(self):
        await websocket.accept()
        self.cam_connections.append(websocket)
        print(f"CAM connected | total: {len(self.cam_connections)}")

    def disconnect_cam(self, websocket: WebSocket):
        self.cam_connections.remove(websocket)
        print(f"CAM disconnected | total: {len(self.cam_connections)}")

    async def send_to_app(self, messsage: dict):
        dead_connection = []

        for connection in self.app_connections:
            try:
                await connection.send_json(messsage)
            except:
                dead_connection.append(connection)

        for conn in dead_connection:
            self.disconnect_cam(conn)

    async  def send_to_cam(self, messsage: dict):
        dead_connection = []

        for connection in self.cam_connections:
            try:
                await connection.send_json(messsage)
            except:
                dead_connection.append(connection)

        for conn in dead_connection:
            self.disconnect_cam(conn)

    async def broadcast_to_app(self, messsage: dict):
        await self.send_to_app(messsage)

    async def broadcast_to_cam(self, messsage: dict):
        await self.send_to_cam(messsage)

manager = ConnectionManager()


