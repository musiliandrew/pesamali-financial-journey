import { usePurchaseItem, useShopItems } from "../hooks/useShop";

export default function Shop() {
  const { items, loading, error } = useShopItems();
  const { purchase, loading: buying, error: buyError } = usePurchaseItem();

  return (
    <div className="min-h-screen p-6 max-w-4xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Shop</h1>

      {loading && <div>Loading...</div>}
      {error && <div className="text-red-400">{error}</div>}

      <div className="grid gap-4 md:grid-cols-2">
        {items.map((it: any) => (
          <div key={it.id} className="p-4 rounded-xl bg-[#1A2332] flex items-center gap-4">
            <div className="w-16 h-16 rounded bg-[#0F1724]" />
            <div className="flex-1">
              <div className="font-semibold">{it.name}</div>
              <div className="text-xs opacity-70">{it.description}</div>
              <div className="text-sm mt-1">{it.rarity || "standard"}</div>
            </div>
            <div className="text-right">
              <div className="text-[#FFEA7A] font-bold">{it.price} pts</div>
              <button
                className="mt-2 px-3 py-2 rounded bg-blue-600 disabled:opacity-50"
                disabled={buying}
                onClick={() => purchase(it.id)}
              >
                {buying ? "Purchasing..." : "Purchase"}
              </button>
              {buyError && <div className="text-red-400 text-xs mt-1">{buyError}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
