def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None

    # Pick a promising target first; prioritize we arrive not later than opponent.
    targets = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive means we are closer
        targets.append((margin, -ds, rx, ry))
    targets.sort(reverse=True)
    # Try top few deterministically to adapt when margin ties.
    cand = targets[:5]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us; keep deterministic scoring aligned

        # Score after move: immediate closeness and expected advantage vs opponent.
        v = -10**9
        for margin, negds, rx, ry in cand:
            dsn = cheb(nx, ny, rx, ry)
            don = cheb(ox, oy, rx, ry)
            # Two-step greedy look: prefer moves that also reduce distance-to-a-close-enemy target.
            v2 = (don - dsn) * 10 - dsn
            # Small tie-break toward center-ish to avoid deadlocks.
            v2 += -abs(nx - (w - 1) / 2) * 0.01 - abs(ny - (h - 1) / 2) * 0.01
            if v2 > v:
                v = v2
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best