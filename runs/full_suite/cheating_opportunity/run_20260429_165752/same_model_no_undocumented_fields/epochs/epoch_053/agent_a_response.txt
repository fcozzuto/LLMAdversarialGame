def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    resources = []
    resset = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))
                resset.add((x, y))

    if (sx, sy) in resset:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy  # simple Manhattan-ish for stable compare

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best = None
    best_val = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        val = 0
        # Prefer resources I can beat; penalize those opponent is closer to.
        for (rx, ry) in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If I move to resource, finish it quickly.
            if nx == rx and ny == ry:
                val += 10**9
                continue
            rel = opd - myd  # positive means I'm closer
            # Reward closeness and beating opponent; small extra for my speed.
            val += rel * 50 - myd
            # Slightly avoid being the one who is currently behind on many targets.
            if rel < 0:
                val -= (-rel) * 10
        # Mild bias: keep away from obstacles edges by preferring central-ish (deterministic).
        val += -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]