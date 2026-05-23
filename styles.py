def load_css():

    return """
    <style>

    .stApp{
        background: linear-gradient(
            135deg,
            #0f172a,
            #1e3a8a,
            #2563eb
        );
        color: white;
    }

    .main-title{
        font-size: 42px;
        font-weight: bold;
        color: white;
        text-align: center;
        margin-bottom: 10px;
    }

    .sub-title{
        text-align:center;
        color:#dbeafe;
        margin-bottom:30px;
    }

    .stTextInput input{
        background-color:#1e293b;
        color:white;
        border-radius:10px;
        border:1px solid #3b82f6;
    }

    .stButton button{
        background-color:#2563eb;
        color:white;
        border:none;
        border-radius:10px;
        padding:10px 20px;
        font-weight:bold;
    }

    .stButton button:hover{
        background-color:#1d4ed8;
    }

    section[data-testid="stSidebar"]{
        background-color:#0f172a;
        color:white;
    }

    .chat-user{
        background:#1e40af;
        padding:12px;
        border-radius:12px;
        margin:8px 0;
    }

    .chat-ai{
        background:#0f172a;
        padding:12px;
        border-radius:12px;
        margin:8px 0;
        border:1px solid #2563eb;
    }

    </style>
    """