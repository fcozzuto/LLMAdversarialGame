def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1, h - 1) if ((sx + sy) % 2 == 0) else (0, 0)
        best = None
        bestd = 10**9
        bestidx = 10**9
        for i, (dx, dy) in enumerate(deltas):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and i < bestidx):
                bestd, bestidx, best = d, i, (dx, dy)
        return list(best if best is not None else (0, 0))

    turns_remaining = int(observation.get("turns_remaining", 0))
    aggressive = 1 if turns_remaining <= 10 else 0  # later: commit more to single best target

    best_move = (0, 0)
    best_val = -10**18
    best_i = 10**9

    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        self_to_opp = cheb(nx, ny, ox, oy)
        # Encourage moves that get us to resources sooner than opponent.
        advantages = []
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            advantages.append(od - sd)

        advantages.sort(reverse=True)
        # Use top-K resources to avoid full-grid computation.
        k = 1 if aggressive else (3 if len(advantages) >= 3 else len(advantages))
        top = advantages[:k]
        # Commit pressure: prefer being close to best target as well.
        best_target_dist = min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        val = 0.0
        # Primary: how much we beat opponent on high-value targets
        for j, a in enumerate(top):
            val += a * (2.2 - 0.35 * j)
        # Secondary: reduce distance to our current best target
        val -= 0.6 * best_target_dist
        # Tertiary: if tie on resource races, avoid walking into being immediately contested
        val -= 0.05 * self_to_opp

        if val > best_val or (val == best_val and i < best_i):
            best_val, best_i, best_move = val, i, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]