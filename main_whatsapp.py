from langgraph_whatsapp.server_whatsapp import app

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        #reload=True,
        #ssl_keyfile="key.pem",
        #ssl_certfile="cert.pem"
    )
