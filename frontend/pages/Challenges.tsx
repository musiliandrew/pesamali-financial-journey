import { useState } from "react";
import { useChallenges, useSendChallenge, useSubmitAnswer } from "../hooks/useQA";

export default function Challenges() {
  const { entries, loading, error, meta, page, setPage } = useChallenges();
  const { send, loading: sending, error: sendError } = useSendChallenge();
  const { submit, loading: answering, error: answerError } = useSubmitAnswer();

  const [toUserId, setToUserId] = useState("");
  const [profession, setProfession] = useState<string>("");

  return (
    <div className="min-h-screen p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Challenges</h1>

      <div className="p-4 rounded bg-[#1A2332] space-y-2">
        <div className="font-semibold">Send a challenge</div>
        <input className="w-full p-2 rounded bg-[#0F1724]" placeholder="Recipient userId" value={toUserId} onChange={e=>setToUserId(e.target.value)} />
        <input className="w-full p-2 rounded bg-[#0F1724]" placeholder="Profession (optional)" value={profession} onChange={e=>setProfession(e.target.value)} />
        <button disabled={sending} className="px-3 py-2 rounded bg-blue-600" onClick={() => send(toUserId, profession || undefined)}>Send</button>
        {sendError && <div className="text-red-400 text-sm">{sendError}</div>}
      </div>

      <div className="p-4 rounded bg-[#1A2332] space-y-3">
        <div className="font-semibold">Your pending challenges</div>
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-400">{error}</div>}
        <div className="space-y-2">
          {entries.map((c:any) => (
            <div key={c.id} className="p-3 rounded bg-[#0F1724]">
              <div className="font-medium">{c.question.question}</div>
              <div className="mt-2 grid gap-2">
                {c.question.options.map((opt:string, idx:number) => (
                  <button key={idx} className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-left"
                    disabled={answering}
                    onClick={() => submit(c.id, idx)}>
                    {idx+1}. {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        {answerError && <div className="text-red-400 text-sm">{answerError}</div>}
        {meta && (
          <div className="flex items-center gap-2 pt-2">
            <button className="px-3 py-1 rounded bg-gray-700" disabled={page<=1} onClick={()=>setPage(page-1)}>Prev</button>
            <div className="text-sm">Page {meta.page} / {Math.ceil(meta.total / meta.page_size) || 1}</div>
            <button className="px-3 py-1 rounded bg-gray-700" disabled={(meta.page*meta.page_size)>=meta.total} onClick={()=>setPage(page+1)}>Next</button>
          </div>
        )}
      </div>
    </div>
  );
}
