def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    resset = set((r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2)
    if (sx, sy) in resset:
        return [0, 0]
    if not resources:
        return [0, 0]

    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                ds = dist(sx, sy, x, y)
                do = dist(ox, oy, x, y)
                cand.append((ds, do, x, y))
    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (t[0] - t[1], t[0], t[2], t[3]))
    cand = cand[:6]

    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Score: prefer targets where we are closer than opponent; then minimize our distance.
        val = 0
        for ds, do, tx, ty in cand:
            new_ds = dist(nx, ny, tx, ty)
            # If opponent is already closer, penalize strongly to avoid "handoffs"
            gap = (do - new_ds)
            val += (0 if gap > 0 else 50) + (new_ds * 3) + (max(0, (new_ds - do)) * 7)
        # small preference for staying when equal
        if best_val is None or val < best_val or (val == best_val and (dx * dx + dy * dy) < (best_move[0] * best_move[0] + best_move[1] * best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]