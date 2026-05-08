def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = [(int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2]

    neigh8 = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    def score_cell(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return -10**9
        adj_opp = any((x + dx, y + dy) in opp_t for dx, dy in neigh8)
        adj_self = any((x + dx, y + dy) in self_t for dx, dy in neigh8)
        dist_opp = abs(x - ox) + abs(y - oy)
        dist_self = abs(x - sx) + abs(y - sy)
        flip_bonus = 3 if (x, y) in opp_t else 0  # mostly unreachable since unclaimed, but safe
        # Prefer frontier captures adjacent to opponent and not too far from us
        return (5 if adj_opp else 0) + (2 if adj_self else 0) + flip_bonus - 0.04 * dist_opp - 0.02 * dist_self

    best = None
    best_sc = -10**18
    candidates = unclaimed
    if not candidates:
        candidates = list(opp_t) if opp_t else [(ox, oy), (sx, sy)]
    # Deterministic tie-breaker: (score desc, -x, -y)
    for x, y in candidates:
        sc = score_cell(x, y)
        if sc > best_sc or (sc == best_sc and ((-x, -y) < (-best[0], -best[1]) if best else True)):
            best_sc = sc
            best = (x, y)

    bx, by = best if best else (sx, sy)
    dx = 0 if bx == sx else (1 if bx > sx else -1)
    dy = 0 if by == sy else (1 if by > sy else -1)

    # If blocked, try alternative deterministic directions toward target (8-way greedy)
    preferred = []
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = sx + ddx, sy + ddy
            if free(tx, ty):
                preferred.append((abs(tx - bx) + abs(ty - by), (ddx, ddy)))
    preferred.sort(key=lambda t: (t[0], -t[1][0], -t[1][1]))
    for _, (ddx, ddy) in preferred[:5]:
        nx, ny = sx + ddx, sy + ddy
        if free(nx, ny):
            return [int(ddx), int(ddy)]

    return [0, 0]