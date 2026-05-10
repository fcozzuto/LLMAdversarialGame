def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(a, b):
        ax, ay = a
        bx, by = b
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    un_list = list(unclaimed)
    opp_list = list(opp_t)

    cand_dirs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if ok(sx + dx, sy + dy):
                cand_dirs.append((dx, dy))

    if not cand_dirs:
        return [0, 0]

    # Precompute nearest target distances (squared)
    # If there are no unclaimed cells, fall back to targeting opponent territory.
    targets_un = un_list
    targets_fallback = opp_list if opp_list else [(ox, oy)]
    best_u0 = min((d2((sx, sy), t) for t in targets_un), default=None)
    best_o0 = min((d2((sx, sy), t) for t in targets_fallback), default=None)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        cell = (nx, ny)

        # Territory value: prefer flipping opponent territory, then unclaimed, then extending self
        if cell in opp_t:
            val = 500
        elif cell in unclaimed:
            val = 200
        elif cell in self_t:
            val = 80
        else:
            val = 40

        # Distance shaping
        nu = min((d2(cell, t) for t in targets_un), default=10**9) if targets_un else 10**9
        no = min((d2(cell, t) for t in targets_fallback), default=10**9)

        # Prefer smaller distance to unclaimed; when none, prefer approaching opponent territory
        approach = -nu if targets_un else -no

        # Slightly prefer moving toward center to avoid being cornered
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Keep pressure: also prefer being closer to opponent head position
        head_pen = d2(cell, (ox, oy))

        # Deterministic tie-break: favor lexicographically smaller (dx,dy)
        score = val + (2.0 * approach) - 0.05 * center_pen - 0.01 * head_pen

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]