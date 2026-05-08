def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    unclaimed = observation.get("unclaimed_cells", []) or []
    self_territory = observation.get("self_territory", []) or []
    opp_territory = observation.get("opponent_territory", []) or []

    self_set = set((a[0], a[1]) for a in self_territory if isinstance(a, (list, tuple)) and len(a) >= 2)
    opp_set = set((a[0], a[1]) for a in opp_territory if isinstance(a, (list, tuple)) and len(a) >= 2)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid_cell(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # Prefer fast expansion into unclaimed; bias away from opponent to avoid immediate loss of tempo.
    opp_anchor = (ox, oy)
    best = None
    best_key = None
    for c in unclaimed:
        if not isinstance(c, (list, tuple)) or len(c) < 2:
            continue
        x, y = c[0], c[1]
        if not valid_cell(x, y):
            continue
        d_self = man((sx, sy), (x, y))
        d_opp = man(opp_anchor, (x, y))
        # Prefer being closer than opponent, and slightly closer overall; deterministic tie-break.
        key = (d_self, -d_opp, x + y * 0.001)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    # If no unclaimed, attempt to enter near opponent territory (diagonal greedy).
    if best is None:
        candidates = []
        for ax, ay in opp_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = ax + dx, ay + dy
                    if valid_cell(nx, ny):
                        candidates.append((nx, ny))
        # Deterministic: unique via set
        cand_set = set(candidates)
        best = None
        best_key = None
        for x, y in cand_set:
            d_self = man((sx, sy), (x, y))
            d_opp = man((ox, oy), (x, y))
            key = (d_self, d_opp, x + y * 0.001)
            if best_key is None or key < best_key:
                best_key = key
                best = (x, y)

    tx, ty = best if best is not None else (sx, sy)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not valid_cell(nx, ny):
        # Try alternate greedy directions deterministically; else stay.
        options = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        moved = False
        for ddx, ddy in options:
            nnx, nny = sx + ddx, sy + ddy
            if valid_cell(nnx, nny):
                return [ddx, ddy]
        return [0, 0]
    return [dx, dy]