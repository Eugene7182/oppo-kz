from fastapi import APIRouter, WebSocket, WebSocketDisconnect
router = APIRouter(prefix="/ws", tags=["ws"])

active = set()

@router.websocket("")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    active.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            # echo/broadcast
            for peer in list(active):
                try:
                    await peer.send_text(data)
                except Exception:
                    pass
    except WebSocketDisconnect:
        active.discard(ws)
