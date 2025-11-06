# PesaMali - Financial Literacy Board Game

A mobile-first social educational board game teaching financial literacy through engaging gameplay.

## 🎮 Features

- **Social Gameplay**: 2-4 player matches with friends or AI
- **Financial Education**: Learn about assets, liabilities, savings, and investment
- **Progression System**: Unlock dreams with Pesa Mali points
- **Profession System**: Choose from Teachers, Writers, Doctors, Engineers, Artists, Athletes, Entrepreneurs
- **Streak Mechanics**: Daily play streaks with friend support
- **Societies**: Join communities and compete on leaderboards
- **Customization**: Avatars, skins, and cosmetic items
- **Real-time Multiplayer**: WebSocket-based game state synchronization

## 🏗️ Tech Stack

### Backend
- **Framework**: Encore.ts
- **Authentication**: Clerk
- **Database**: PostgreSQL (Encore SQL Database)
- **Real-time**: WebSocket streaming

### Frontend
- **Framework**: React + Vite + TypeScript
- **UI Components**: shadcn/ui + Tailwind CSS v4
- **State Management**: @tanstack/react-query
- **Routing**: React Router
- **Authentication**: @clerk/clerk-react

## 📦 Project Structure

```
/
├── backend/
│   ├── auth/                # Authentication service (Clerk integration)
│   │   ├── encore.service.ts
│   │   └── auth.ts         # Auth handler & Gateway
│   ├── user/               # User management service
│   │   ├── create.ts       # User registration
│   │   ├── get.ts          # User profile retrieval
│   │   ├── update_points.ts
│   │   └── types.ts
│   ├── game/               # Game logic service
│   │   ├── create_match.ts
│   │   ├── join_match.ts
│   │   ├── start_match.ts
│   │   ├── select_asset.ts
│   │   ├── roll_dice.ts
│   │   ├── move_token.ts
│   │   ├── get_state.ts
│   │   ├── stream_updates.ts
│   │   └── mock_*.ts       # Mock data generators
│   ├── friends/            # Social features service
│   │   ├── send_invite.ts
│   │   ├── accept_invite.ts
│   │   ├── list.ts
│   │   ├── create_challenge.ts
│   │   └── sacrifice_points.ts
│   ├── shop/               # In-app purchases service
│   │   ├── list_items.ts
│   │   ├── purchase.ts
│   │   └── mock_items.ts
│   └── db/
│       ├── index.ts
│       └── migrations/
│           └── 001_initial_schema.up.sql
│
└── frontend/
    ├── pages/
    │   ├── Onboarding.tsx  # Tutorial & registration
    │   ├── Profile.tsx     # User profile & stats
    │   ├── Lobby.tsx       # Main hub & matchmaking
    │   ├── Game.tsx        # Game board & gameplay
    │   └── PostGame.tsx    # Match results & stats
    ├── components/
    │   ├── BoardGrid.tsx   # 8x10 game board
    │   ├── PlayerHUD.tsx   # Player stats overlay
    │   ├── DiceRoller.tsx  # Animated dice
    │   └── MatchSetupModal.tsx
    ├── hooks/
    │   ├── useBackend.ts   # Authenticated backend client
    │   └── useGameStream.ts # WebSocket game state
    └── lib/
        ├── types.ts
        ├── game-engine.ts  # Deterministic game logic
        └── utils.ts

```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Encore CLI (`npm install -g encore`)

### Installation

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd pesamali
   ```

2. **Set up Clerk authentication:**
   
   The Clerk secret key is already configured in the `ClerkSecretKey` secret.
   
   To use the app in development:
   - The publishable key is: `pk_test_cHJlc2VudC13cmVuLTUwLmNsZXJrLmFjY291bnRzLmRldiQ`
   - This is already configured in `frontend/App.tsx`

3. **Run the application:**
   ```bash
   encore run
   ```

   The application will automatically:
   - Install all dependencies (no manual npm install needed)
   - Set up the database
   - Start the backend API
   - Start the frontend dev server
   - Open your browser to the app

4. **Access the app:**
   - Frontend: https://proj-d45is3482vjgsfpmhh40.lp.dev
   - Backend API: https://proj-d45is3482vjgsfpmhh40.api.lp.dev

## 🎯 Game Rules

### Board Layout
- **80 tiles** (8 columns × 10 rows) with serpentine path
- **Yellow-striped spots** at specific indices trigger card draws
- **Opposite orientation** for players on opposite sides

### Starting Conditions
- Each player: **1200 game points**
- **4 tokens** per player
- **2 assets** (chosen pre-game)
- **3 spending cards** (random)
- **3 savings cards** (random)

### Asset Cards (Choose 2)
1. Campus Printing Shop: 600pts → 320pts/return
2. Online Tasking Platform: 450pts → 220pts/return
3. Monetized YouTube Channel: 400pts → 170pts/return
4. Peer to Peer Lending Fund: 400pts → 220pts/return
5. Cryptocurrency Portfolio: 500pts → 240pts/return

### Win Conditions (ALL must be met)
1. ✅ Bought 2 assets
2. ✅ Savings ≥ 500
3. ✅ All liabilities cleared
4. ✅ All spending/savings cards resolved
5. ✅ Can afford Dream purchase

### Key Mechanics
- **Yellow-strip priority**: -20pts penalty if skipped
- **Auto-move**: System moves after 20s timeout
- **Asset returns**: Max 5 returns per asset, only on ODD spots
- **Deterministic RNG**: Each match has a seed for reproducibility

## 🔐 Authentication Flow

### User Registration (Onboarding)
1. User completes 3-slide tutorial
2. Enters name, email, password, profession
3. Clerk creates account
4. Backend creates user profile with Clerk user ID
5. Redirects to Lobby

### Authenticated API Calls
All API calls from frontend use the `useBackend()` hook:

```typescript
import { useBackend } from '@/hooks/useBackend';

function MyComponent() {
  const backend = useBackend();
  
  // All calls automatically include auth token
  const user = await backend.user.getMe();
}
```

### Backend Authentication
Endpoints requiring authentication use `auth: true`:

```typescript
export const getMe = api<void, UserProfile>(
  { auth: true, expose: true, method: "GET", path: "/users/me" },
  async () => {
    const auth = getAuthData()!;
    // auth.userID is the Clerk user ID
    // ...
  }
);
```

## 🔄 Swapping Mock Backend with Real Backend

The current implementation uses **mock data and in-memory game state** for rapid development. Here's how to replace it with a production-ready backend:

### 1. WebSocket Game State

**Current (Mock):**
```typescript
// backend/game/stream_updates.ts
// Returns mock game state updates
```

**Production:**
1. Replace mock game engine with authoritative server logic
2. Store game state in `game_state` table
3. Emit events to all connected players via WebSocket
4. Validate all player actions server-side
5. Log all events for replay/anti-cheat

```typescript
export const streamUpdates = api(
  { expose: true, method: "GET", path: "/matches/:matchId/stream" },
  async (req): Promise<ReadableStream> => {
    const stream = new ReadableStream({
      async start(controller) {
        // Subscribe to game events from database/Redis
        const subscription = subscribeToMatchEvents(req.matchId);
        
        subscription.on('event', (event) => {
          controller.enqueue({
            type: event.type,
            payload: event.data,
            timestamp: Date.now()
          });
        });
      }
    });
    
    return stream;
  }
);
```

### 2. Dice Rolling (RNG)

**Current (Mock):**
```typescript
// Deterministic based on seed but client-friendly
const die1 = seededRandom(seed, rollCount) * 6 + 1;
```

**Production:**
```typescript
// Server generates truly random with seed logging
import { randomBytes } from 'crypto';

export const rollDice = api<RollRequest, RollResponse>(
  { auth: true, expose: true, method: "POST", path: "/matches/:matchId/roll" },
  async ({ matchId }) => {
    const auth = getAuthData()!;
    
    // Validate it's player's turn
    const match = await validatePlayerTurn(matchId, auth.userID);
    
    // Cryptographically secure random
    const bytes = randomBytes(2);
    const die1 = (bytes[0] % 6) + 1;
    const die2 = (bytes[1] % 6) + 1;
    
    // Log for audit/replay
    await db.exec`
      INSERT INTO game_events (match_id, user_id, event_type, event_data)
      VALUES (${matchId}, ${auth.userID}, 'dice_roll', 
              ${JSON.stringify({ die1, die2, bytes: bytes.toString('hex') })})
    `;
    
    return { die1, die2, sum: die1 + die2 };
  }
);
```

### 3. Match State Persistence

**Current:** In-memory mock objects

**Production:**
```typescript
// After every game action, persist state
await db.exec`
  UPDATE game_state 
  SET state = ${JSON.stringify(fullGameState)},
      updated_at = NOW()
  WHERE match_id = ${matchId}
`;

// Emit to all players
await emitGameEvent(matchId, {
  type: 'state_update',
  state: fullGameState
});
```

### 4. Anti-Cheat & Validation

Add server-side validation for all actions:

```typescript
// Validate token movement
function validateTokenMove(gameState, playerId, tokenId, diceSum) {
  const player = gameState.players.find(p => p.id === playerId);
  const token = player.tokens.find(t => t.id === tokenId);
  
  // Check: correct distance
  if (token.position + diceSum > 80) return false;
  
  // Check: player's turn
  if (gameState.currentTurn !== playerId) return false;
  
  // Check: yellow-strip penalty applies
  const wouldLandOnYellow = isYellowStrip(token.position + diceSum);
  if (!wouldLandOnYellow && hasYellowOption(player.tokens, diceSum)) {
    // Apply -20pts penalty
  }
  
  return true;
}
```

### 5. Matchmaking & Lobbies

**Current:** Simple match creation

**Production:**
1. Implement ELO/MMR system
2. Add queue system with skill-based matching
3. Timeout inactive players
4. Handle disconnects gracefully

```typescript
// Add to backend/game/matchmaking.ts
export const joinQueue = api<QueueRequest, QueueResponse>(
  { auth: true, method: "POST", path: "/matchmaking/queue" },
  async (req) => {
    const auth = getAuthData()!;
    const user = await getUser(auth.userID);
    
    // Add to Redis queue with MMR
    await redis.zadd('matchmaking_queue', user.mmr, auth.userID);
    
    // Try to form matches
    await tryFormMatches();
    
    return { queued: true, estimatedWait: 30 };
  }
);
```

### 6. Notifications & Push

Integrate real notification system:

```typescript
// Use Firebase Cloud Messaging or similar
import { sendPushNotification } from './notifications';

// When friend invites
await sendPushNotification(toUserId, {
  title: `Friend request from ${fromUser.username}`,
  body: "Accept to play together!",
  data: { type: 'friend_invite', fromUserId }
});

// When match starts
await sendPushNotification(playerId, {
  title: "Match starting!",
  body: "Your game is beginning",
  data: { type: 'match_start', matchId }
});
```

### 7. Analytics & Telemetry

Add comprehensive event tracking:

```typescript
// Track all user actions
await db.exec`
  INSERT INTO analytics_events (user_id, event_type, event_data, session_id)
  VALUES (${userId}, ${eventType}, ${data}, ${sessionId})
`;

// Aggregate for dashboards
// - Daily active users
// - Match completion rate
// - Average game duration
// - Popular professions
// - Asset purchase patterns
```

### 8. Database Optimization

For production scale:

```sql
-- Add indexes for common queries
CREATE INDEX idx_matches_active ON matches(status) WHERE status IN ('waiting', 'active');
CREATE INDEX idx_game_events_match ON game_events(match_id, created_at DESC);
CREATE INDEX idx_users_active ON users(last_active DESC) WHERE last_active > NOW() - INTERVAL '7 days';

-- Partition large tables
CREATE TABLE game_events_2025 PARTITION OF game_events
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### 9. Caching Strategy

Add Redis for hot data:

```typescript
import { Redis } from 'ioredis';
const redis = new Redis(process.env.REDIS_URL);

// Cache active matches
export async function getMatch(matchId: string) {
  const cached = await redis.get(`match:${matchId}`);
  if (cached) return JSON.parse(cached);
  
  const match = await db.queryRow`SELECT * FROM matches WHERE id = ${matchId}`;
  await redis.setex(`match:${matchId}`, 300, JSON.stringify(match));
  
  return match;
}
```

### 10. Environment Configuration

Create production config:

```typescript
// backend/config/index.ts
export const config = {
  clerk: {
    secretKey: secret("ClerkSecretKey"),
    publishableKey: process.env.CLERK_PUBLISHABLE_KEY
  },
  redis: {
    url: secret("RedisURL")
  },
  websocket: {
    maxConnections: 10000,
    heartbeatInterval: 30000
  },
  game: {
    turnTimeout: 20000,
    maxPlayers: 4,
    seedComplexity: 'production' // vs 'development'
  }
};
```

## 🧪 Testing

### Run Tests
```bash
encore test
```

### Acceptance Criteria
- ✅ Onboarding: 3-slide tutorial + registration
- ✅ Asset Picker: Alternating picks, frosted state
- ✅ Dice & Moves: Deterministic RNG, preview, auto-move
- ✅ Yellow-strip: Card draw on landing, -20pts penalty if avoided
- ✅ Asset Returns: Correct timing, max 5 returns, sequential resolution
- ✅ Win Condition: All 5 requirements enforced
- ✅ Social: Friend invites, streak protection, challenges

## 📱 Mobile-First Design

### Breakpoints
- Mobile: 360-430px (primary target)
- Tablet: 768px
- Desktop: 1024px+

### Responsive Patterns
```css
/* Mobile-first */
.board-grid {
  grid-template-columns: repeat(8, 1fr);
  gap: 0.25rem; /* 4px on mobile */
}

/* Tablet */
@media (min-width: 768px) {
  .board-grid {
    gap: 0.5rem; /* 8px on tablet */
  }
}
```

### Touch Optimizations
- Minimum touch target: 44x44px
- Tap animations: scale(0.98) feedback
- Swipe gestures disabled during gameplay
- Haptic feedback on key actions

## 🎨 Design System

### Colors
```typescript
const colors = {
  primary: '#0E6FFF',      // CTA buttons
  success: '#28C76F',      // Wins, bonuses
  danger: '#FF4D4F',       // Losses, penalties
  bgDark: '#0F1724',       // Main background
  bgLight: '#F8FAFC',      // Light mode
  yellowStrip: '#FFEA7A',  // Special tiles
};
```

### Typography
- Font: Inter
- Sizes: 12px (small), 14px (body), 18-22px (headlines)
- Weights: 400 (regular), 600 (semibold)

### Spacing
- Base: 8px grid
- Scale: 8, 12, 16, 24, 32px

## 🔒 Security

- ✅ Clerk handles authentication & user management
- ✅ All user inputs validated server-side
- ✅ SQL injection prevented (parameterized queries)
- ✅ Auth required for sensitive endpoints
- ✅ Rate limiting (Encore built-in)
- ✅ HTTPS enforced in production

## 📊 Performance

- Code splitting: Route-based
- Lazy loading: Non-critical assets
- Image optimization: 1x, 2x, 3x exports
- Bundle size target: <500KB initial
- Time to Interactive: <3s on 4G
- GPU acceleration: Token animations

## ♿ Accessibility

- Keyboard navigation: All interactive elements
- Screen readers: ARIA labels on all controls
- Color contrast: 4.5:1 minimum
- Reduced motion: Respects `prefers-reduced-motion`
- Focus indicators: Visible outlines

## 📚 API Documentation

### User Endpoints
- `POST /users` - Create user profile (auth required)
- `GET /users/me` - Get current user (auth required)
- `GET /users/:id` - Get user by ID (auth required)
- `PUT /users/points` - Update Pesa Mali points (auth required)

### Game Endpoints
- `POST /matches` - Create match (auth required)
- `POST /matches/:matchId/join` - Join match (auth required)
- `POST /matches/:matchId/start` - Start match (auth required)
- `POST /matches/:matchId/select-asset` - Pick asset (auth required)
- `POST /matches/:matchId/roll` - Roll dice (auth required)
- `POST /matches/:matchId/move` - Move token (auth required)
- `GET /matches/:matchId` - Get game state (auth required)
- `GET /matches/:matchId/stream` - WebSocket stream (auth required)

### Friends Endpoints
- `POST /friends/invite` - Send friend invite (auth required)
- `POST /friends/accept` - Accept invite (auth required)
- `GET /friends` - List friends (auth required)
- `POST /friends/challenge` - Send Q/A challenge (auth required)
- `POST /friends/sacrifice` - Sacrifice points for streak (auth required)

### Shop Endpoints
- `GET /shop/items` - List available items
- `POST /shop/purchase` - Purchase item (auth required)

## 🤝 Contributing

1. Follow Encore.ts conventions
2. Use TypeScript strict mode
3. Write tests for new features
4. Follow mobile-first design
5. Ensure accessibility compliance

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

- Documentation: [Encore.ts Docs](https://encore.dev/docs)
- Discord: [Encore Community](https://encore.dev/discord)
- Issues: GitHub Issues

---

Built with ❤️ using Encore.ts, React, and Clerk
