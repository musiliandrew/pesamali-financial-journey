import { useState } from "react";
import { useAdminQuestions } from "../hooks/useAdminQA";
import { useAdminAssets, useAdminEventCards, useAdminSavingsCards, useAdminSpendingCards } from "../hooks/useAdminCards";
import { useAdminDreams } from "../hooks/useAdminDreams";
import { useAdminShop } from "../hooks/useAdminShop";

function Section({ title, children }: { title: string; children: any }) {
  return (
    <div className="p-4 rounded-xl bg-[#1A2332] space-y-3">
      <div className="text-lg font-semibold">{title}</div>
      {children}
    </div>
  );
}

export default function Admin() {
  const [tab, setTab] = useState<'qa'|'cards'|'dreams'|'shop'>('qa');
  const [cardsTab, setCardsTab] = useState<'assets'|'event'|'savings'|'spending'>('assets');

  // QA
  const qa = useAdminQuestions();

  // Cards
  const assets = useAdminAssets();
  const eventCards = useAdminEventCards();
  const savingsCards = useAdminSavingsCards();
  const spendingCards = useAdminSpendingCards();

  // Dreams
  const dreams = useAdminDreams();

  // Shop
  const shop = useAdminShop();

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Admin</h1>

      <div className="flex gap-2">
        <button className={`px-3 py-2 rounded ${tab==='qa'?'bg-blue-600':''}`} onClick={()=>setTab('qa')}>QA</button>
        <button className={`px-3 py-2 rounded ${tab==='cards'?'bg-blue-600':''}`} onClick={()=>setTab('cards')}>Cards</button>
        <button className={`px-3 py-2 rounded ${tab==='dreams'?'bg-blue-600':''}`} onClick={()=>setTab('dreams')}>Dreams</button>
        <button className={`px-3 py-2 rounded ${tab==='shop'?'bg-blue-600':''}`} onClick={()=>setTab('shop')}>Shop</button>
      </div>

      {tab==='qa' && (
        <Section title="QA Questions">
          {qa.error && <div className="text-red-400 text-sm">{qa.error}</div>}
          <QAForm onCreate={qa.create} />
          <div className="space-y-2">
            {qa.items.map((q:any)=> (
              <div key={q.id} className="p-3 rounded bg-[#0F1724] flex items-start justify-between gap-3">
                <div>
                  <div className="font-semibold">[{q.profession}] {q.question}</div>
                  <div className="text-xs opacity-70">Ans: {q.correct_option+1}</div>
                </div>
                <button className="px-2 py-1 rounded bg-red-600" onClick={()=>qa.remove(q.id)}>Delete</button>
              </div>
            ))}
          </div>
        </Section>
      )}

      {tab==='cards' && (
        <div className="space-y-3">
          <div className="flex gap-2">
            <button className={`px-3 py-1 rounded ${cardsTab==='assets'?'bg-blue-600':''}`} onClick={()=>setCardsTab('assets')}>Assets</button>
            <button className={`px-3 py-1 rounded ${cardsTab==='event'?'bg-blue-600':''}`} onClick={()=>setCardsTab('event')}>Event</button>
            <button className={`px-3 py-1 rounded ${cardsTab==='savings'?'bg-blue-600':''}`} onClick={()=>setCardsTab('savings')}>Savings</button>
            <button className={`px-3 py-1 rounded ${cardsTab==='spending'?'bg-blue-600':''}`} onClick={()=>setCardsTab('spending')}>Spending</button>
          </div>

          {cardsTab==='assets' && (
            <Section title="Asset Cards">
              <AssetForm onCreate={assets.create} />
              <ListSimple items={assets.items} onDelete={assets.remove} display={(i:any)=> `${i.name} | cost ${i.purchase_cost} | profit ${i.profit_per_return}`} />
            </Section>
          )}
          {cardsTab==='event' && (
            <Section title="Event Cards">
              <EventForm onCreate={eventCards.create} />
              <ListSimple items={eventCards.items} onDelete={eventCards.remove} display={(i:any)=> `${i.title} | effect ${i.effect_points}`} />
            </Section>
          )}
          {cardsTab==='savings' && (
            <Section title="Savings Cards">
              <SavingsForm onCreate={savingsCards.create} />
              <ListSimple items={savingsCards.items} onDelete={savingsCards.remove} display={(i:any)=> `${i.name} | >= ${i.save_threshold}`} />
            </Section>
          )}
          {cardsTab==='spending' && (
            <Section title="Spending Cards">
              <SpendingForm onCreate={spendingCards.create} />
              <ListSimple items={spendingCards.items} onDelete={spendingCards.remove} display={(i:any)=> `${i.name} | total ${i.total_cost}`} />
            </Section>
          )}
        </div>
      )}

      {tab==='dreams' && (
        <Section title="Dreams">
          <DreamForm onCreate={dreams.create} />
          <ListSimple items={dreams.items} onDelete={dreams.remove} display={(d:any)=> `${d.name} | cost ${d.cost} | slug ${d.slug}`} />
        </Section>
      )}

      {tab==='shop' && (
        <Section title="Shop Items">
          <ShopForm onCreate={shop.create} />
          <ListSimple items={shop.items} onDelete={shop.remove} display={(i:any)=> `${i.name} | ${i.price} pts | ${i.rarity || 'standard'}`} />
        </Section>
      )}
    </div>
  );
}

function ListSimple({ items, onDelete, display }:{ items:any[]; onDelete:(id:string)=>void; display:(i:any)=>string; }){
  return (
    <div className="space-y-2">
      {items.map((i:any)=> (
        <div key={i.id} className="p-3 bg-[#0F1724] rounded flex items-center justify-between">
          <div>{display(i)}</div>
          <button className="px-2 py-1 rounded bg-red-600" onClick={()=>onDelete(i.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

function QAForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [profession, setProfession] = useState('any');
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState<string>('');
  const [correct, setCorrect] = useState(0);
  const [difficulty, setDifficulty] = useState(1);
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-5 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="profession" value={profession} onChange={e=>setProfession(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120] md:col-span-2" placeholder="question" value={question} onChange={e=>setQuestion(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" placeholder="options (comma-separated)" value={options} onChange={e=>setOptions(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="correct idx" value={correct} onChange={e=>setCorrect(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="difficulty" value={difficulty} onChange={e=>setDifficulty(parseInt(e.target.value||'1'))} />
      <button className="px-3 py-2 rounded bg-blue-600 md:col-span-5" onClick={()=> onCreate({ profession, question, options: options.split(',').map(s=>s.trim()), correct_option: correct, difficulty })}>Create</button>
    </div>
  );
}

function AssetForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [name, setName] = useState('');
  const [purchase_cost, setPC] = useState(0);
  const [profit_per_return, setPPR] = useState(0);
  const [max_returns, setMR] = useState(5);
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-5 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="name" value={name} onChange={e=>setName(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="purchase cost" value={purchase_cost} onChange={e=>setPC(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="profit per return" value={profit_per_return} onChange={e=>setPPR(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="max returns" value={max_returns} onChange={e=>setMR(parseInt(e.target.value||'5'))} />
      <button className="px-3 py-2 rounded bg-blue-600 md:col-span-5" onClick={()=> onCreate({ name, purchase_cost, profit_per_return, max_returns })}>Create</button>
    </div>
  );
}

function EventForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [title, setTitle] = useState('');
  const [effect_points, setEP] = useState(0);
  const [message, setMessage] = useState('');
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-5 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="title" value={title} onChange={e=>setTitle(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="effect points" value={effect_points} onChange={e=>setEP(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120] md:col-span-3" placeholder="message" value={message} onChange={e=>setMessage(e.target.value)} />
      <button className="px-3 py-2 rounded bg-blue-600 md:col-span-5" onClick={()=> onCreate({ title, effect_points, message })}>Create</button>
    </div>
  );
}

function SavingsForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [name, setName] = useState('');
  const [save_threshold, setST] = useState(0);
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-3 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="name" value={name} onChange={e=>setName(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="threshold" value={save_threshold} onChange={e=>setST(parseInt(e.target.value||'0'))} />
      <button className="px-3 py-2 rounded bg-blue-600" onClick={()=> onCreate({ name, save_threshold })}>Create</button>
    </div>
  );
}

function SpendingForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [name, setName] = useState('');
  const [total_cost, setTC] = useState(0);
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-3 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="name" value={name} onChange={e=>setName(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="total cost" value={total_cost} onChange={e=>setTC(parseInt(e.target.value||'0'))} />
      <button className="px-3 py-2 rounded bg-blue-600" onClick={()=> onCreate({ name, total_cost })}>Create</button>
    </div>
  );
}

function DreamForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [cost, setCost] = useState(0);
  const [order_index, setOrder] = useState(0);
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-5 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="name" value={name} onChange={e=>setName(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" placeholder="slug" value={slug} onChange={e=>setSlug(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="cost" value={cost} onChange={e=>setCost(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="order" value={order_index} onChange={e=>setOrder(parseInt(e.target.value||'0'))} />
      <button className="px-3 py-2 rounded bg-blue-600 md:col-span-5" onClick={()=> onCreate({ name, slug, cost, order_index })}>Create</button>
    </div>
  );
}

function ShopForm({ onCreate }:{ onCreate:(p:any)=>void }){
  const [name, setName] = useState('');
  const [price, setPrice] = useState(0);
  const [rarity, setRarity] = useState('');
  return (
    <div className="p-3 rounded bg-[#0F1724] grid md:grid-cols-4 gap-2">
      <input className="p-2 rounded bg-[#0B1120]" placeholder="name" value={name} onChange={e=>setName(e.target.value)} />
      <input className="p-2 rounded bg-[#0B1120]" type="number" placeholder="price" value={price} onChange={e=>setPrice(parseInt(e.target.value||'0'))} />
      <input className="p-2 rounded bg-[#0B1120]" placeholder="rarity" value={rarity} onChange={e=>setRarity(e.target.value)} />
      <button className="px-3 py-2 rounded bg-blue-600" onClick={()=> onCreate({ name, price, rarity })}>Create</button>
    </div>
  );
}
