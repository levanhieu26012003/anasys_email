from fastapi import FastAPI, Request
import uvicorn
import google.generativeai as genai
import requests

app = FastAPI()

genai.configure(api_key="AIzaSyCQ8goTqlpw_H39rLbiM1tyCvIZjeo-Xr4")
model = genai.GenerativeModel('gemini-2.0-flash')



def generate_reply(email_content):
    prompt = f"""
        Bạn là trợ lý CSKH. Viết một phản hồi lịch sự và chuyên nghiệp cho email sau, bằng ngôn ngữ HTML. 

        Chỉ xuất nội dung HTML, không bao quanh bằng dấu ```html``` hoặc bất kỳ ký hiệu markdown nào. Không thêm phần giải thích.

        Email:
        \"\"\"
        {email_content}
        \"\"\"

        Phản hồi (HTML):      
        """
    response = model.generate_content(prompt)
    return response.text
@app.post("/ai-agent")
async def receive_from_n8n(req: Request):
    data = await req.json()
    print("📩 emai nhận từ n8n: ", data)
    
    original_text = data.get("text", "")
    from_email = data.get("from","")
    subject = data.get("subject", "Re: Phản hồi từ hệ thông AI")
    
    ai_reply_origin = generate_reply(original_text)
    
    ai_reply = ai_reply_origin[7:-3]
    print(ai_reply)
    send_to_n8n(from_email, subject, ai_reply)
    return {"status":"ok","reply": ai_reply}

def send_to_n8n(to_email, subject, content):
    payload = {
        "to": to_email,
        "subject":subject,
        "text": content
    }
    
    
    res = requests.post("http://localhost:5678/webhook/send-reply", json=payload)
    print("Đã phản hồi đến n8n:", res.status_code)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)