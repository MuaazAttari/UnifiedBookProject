// import React, { useState } from "react";

// type ChatMessage = {
//   role: "user" | "assistant";
//   content: string;
// };

// const SESSION_ID = "frontend-demo-session";

// const ChatWidget: React.FC = () => {
//   const [messages, setMessages] = useState<ChatMessage[]>([]);
//   const [input, setInput] = useState("");
//   const [loading, setLoading] = useState(false);

//   const sendMessage = async () => {
//     if (!input.trim()) return;

//     const userMessage: ChatMessage = {
//       role: "user",
//       content: input,
//     };

//     setMessages((prev) => [...prev, userMessage]);
//     setInput("");
//     setLoading(true);

//     try {
//       const res = await fetch("http://127.0.0.1:8000/api/v1/chat", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           message: userMessage.content,
//           session_id: SESSION_ID,
//         }),
//       });

//       const data = await res.json();

//       const botMessage: ChatMessage = {
//         role: "assistant",
//         content: data.reply,
//       };

//       setMessages((prev) => [...prev, botMessage]);
//     } catch (err) {
//       console.error("Chat error", err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div style={{ border: "1px solid #ccc", padding: 16, maxWidth: 500 }}>
//       <div style={{ minHeight: 200 }}>
//         {messages.map((msg, i) => (
//           <div key={i} style={{ marginBottom: 8 }}>
//             <strong>{msg.role === "user" ? "You" : "Bot"}:</strong>{" "}
//             {msg.content}
//           </div>
//         ))}

//         {loading && <p>Bot is typing...</p>}
//       </div>

//       <input
//         value={input}
//         onChange={(e) => setInput(e.target.value)}
//         placeholder="Ask something..."
//         style={{ width: "100%", marginTop: 8 }}
//       />

//       <button onClick={sendMessage} style={{ marginTop: 8 }}>
//         Send
//       </button>
//     </div>
//   );
// };

// export default ChatWidget;


import React, { useState } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

const SESSION_ID = "frontend-demo-session";

const ChatWidget: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
  if (!input.trim()) return;

  const userMessage: ChatMessage = {
    role: "user",
    content: input,
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setLoading(true);

  try {
    const res = await fetch("http://localhost:8000/api/routes/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query_text: input,
        session_id: SESSION_ID,
      }),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    const botMessage: ChatMessage = {
      role: "assistant",
      content: data.answer,
    };

    setMessages((prev) => [...prev, botMessage]);
  } catch (err) {
    console.error("Chat error", err);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "Backend error. Check server logs." },
    ]);
  } finally {
    setLoading(false);
  }
};


  return (
    <div style={{ border: "1px solid #ccc", padding: 16, maxWidth: 400 }}>
      <h3>Ask the Book</h3>

      <div style={{ minHeight: 200, marginBottom: 8 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 6 }}>
            <strong>{msg.role === "user" ? "You" : "Bot"}:</strong>{" "}
            {msg.content}
          </div>
        ))}

        {loading && <p>Bot is typing...</p>}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask something..."
        style={{ width: "100%", padding: 6 }}
        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
      />

      <button onClick={sendMessage} style={{ marginTop: 8, width: "100%" }}>
        Send
      </button>
    </div>
  );
};

export default ChatWidget;
