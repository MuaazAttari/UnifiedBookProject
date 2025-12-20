// import React, { useState } from "react";

// export default function ChatTest() {
//   const [message, setMessage] = useState<string>("");
//   const [reply, setReply] = useState<string>("");

//   const sendMessage = async (): Promise<void> => {
//     const res = await fetch("http://127.0.0.1:8000/api/v1/chat", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({
//         message,
//         session_id: "frontend-test",
//       }),
//     });

//     const data = await res.json();
//     setReply(data.reply);
//   };

//   return (
//     <div style={{ padding: "2rem" }}>
//       <h1>Chat Backend Test</h1>

//       <input
//         value={message}
//         onChange={(e) => setMessage(e.target.value)}
//         placeholder="Type message"
//         style={{ width: "300px", padding: "8px" }}
//       />

//       <br /><br />

//       <button onClick={sendMessage}>Send</button>

//       <p><strong>Reply:</strong> {reply}</p>
//     </div>
//   );
// }


// my-website/src/pages/chat-test.tsx

import React, { useState } from "react";

export default function ChatTest() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = async () => {
    setLoading(true);
    setError("");
    setReply("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query_text: message,          // ✅ backend expects this
          session_id: "frontend-test",
          mode: "full_book"              // ✅ required
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }

      const data = await res.json();

      // backend returns `answer`
      setReply(data.answer);

    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: 600 }}>
      <h1>RAG Chatbot Test</h1>

      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask something about the book"
        style={{ width: "100%", padding: "10px" }}
      />

      <br /><br />

      <button onClick={sendMessage} disabled={loading}>
        {loading ? "Sending..." : "Send"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "1rem" }}>
          Error: {error}
        </p>
      )}

      {reply && (
        <p style={{ marginTop: "1rem" }}>
          <strong>Reply:</strong><br />
          {reply}
        </p>
      )}
    </div>
  );
}
