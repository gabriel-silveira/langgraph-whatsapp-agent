from src.langgraph_whatsapp.server_whatsapp import APP

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_whatsapp:APP",
        host="0.0.0.0",
        port=8082,
        reload=True,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )
