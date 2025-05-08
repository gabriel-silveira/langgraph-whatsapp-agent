from langgraph_whatsapp.server_twilio import APP

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(APP, host="0.0.0.0", port=8000, reload=True)
