def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    self_t = set((int(c[0]), int(c[1])) for c in (observation.get("self_territory") or []) if c and len(c) >= 2)
    opp_t = set((int(c[0]), int(c[1])) for c in (observation.get("opponent_territory") or []) if c and len(c) >= 2)
    unclaimed = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    def is_adj_to_self(x, y):
        return any((sx + dx, sy + dy) == (x, y) for dx, dy in neigh)

    candidates = []
    for (x, y) in unclaimed:
        if free(x, y):
            d = abs(x - sx) + abs(y - sy)
            if d <= 4:
                bonus = 0.0
                if observation.get("turn_index", 0) % 10 == 9 and d <= 2:
                    bonus += 0.25
                candidates.append(("unclaimed", x, y, d, bonus))
    for (x, y) in opp_t:
        if free(x, y):
            d = abs(x - sx) + abs(y - sy)
            if d <= 2 and (is_adj_to_self(x, y) or d == 1):
                candidates.append(("attack", x, y, d, 0.0))

    if not candidates:
        for (x, y) in unclaimed:
            if free(x, y):
                d = abs(x - sx) + abs(y - sy)
                if d <= 8:
                    candidates.append(("unclaimed", x, y, d, 0.0))
        if not candidates:
            return [0, 0]

    def key(item):
        typ, x, y, d, bonus = item
        # Prefer attack if available; otherwise nearest unclaimed. Deterministic tie-breaks.
        typ_score = 0 if typ == "attack" else 1
        return (typ_score, d, -bonus, x, y)
    _, tx, ty, _, _ = min(candidates, key=key)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    steps = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mdx, mdy in steps:
        nx, ny = sx + mdx, sy + mdy
        if free(nx, ny):
            return [int(mdx), int(mdy)]
    return [0, 0]