def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []) if x is not None)
    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs_diag = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    dirs8 = dirs4 + dirs_diag + [(0, 0)]

    opp_front = []
    for x, y in opp_t:
        for dx, dy in (dirs4 + dirs_diag):
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in self_t:
                opp_front.append((nx, ny))
    if opp_front:
        # prioritize likely expansion: unclaimed first, then border of opponent
        targets = [c for c in opp_front if c in unclaimed or c in opp_t]
        if targets:
            tx, ty = min(targets, key=lambda c: (0 if c in unclaimed else 1, abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))
        else:
            tx, ty = min(set(opp_front), key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))
    else:
        candidates = [c for c in (observation.get("unclaimed_cells") or []) if c is not None]
        if candidates:
            candidates = [(int(x), int(y)) for x, y in candidates if inb(int(x), int(y)) and (int(x), int(y)) not in obstacles]
            if not candidates:
                return [0, 0]
            tx, ty = min(candidates, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[1], c[0]))
        else:
            # fallback: head toward opponent position (if available) or stay
            op = observation.get("opponent_position") or (w - 1, h - 1)
            tx, ty = int(op[0]), int(op[1])

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal step is blocked, try axis steps deterministically
    nx, ny = sx + dx, sy + dy
    if (dx != 0 and dy != 0) and (not inb(nx, ny) or (nx, ny) in obstacles):
        if not inb(sx + dx, sy) or (sx + dx, sy) in obstacles:
            dx = 0
        if not inb(sx, sy + dy) or (sx, sy + dy) in obstacles:
            dy = 0
        nx, ny = sx + dx, sy + dy

    # Validate final; if invalid, pick best available neighbor toward (tx,ty)
    if not inb(nx, ny) or (nx, ny) in obstacles:
        best = (10**9, 0, 0)
        for ddx, ddy in dirs8:
            if ddx == 0 and ddy == 0:
                cand = (abs(sx - tx) + abs(sy - ty), 2, 0)
                if cand < best:
                    best = cand
                    dx, dy = 0, 0
                continue
            cx, cy = sx + ddx, sy + ddy
            if not inb(cx, cy) or (cx, cy) in obstacles:
                continue
            # prefer entering opponent/unclaimed, then distance
            score = (0 if (cx, cy) in unclaimed else (1 if (cx, cy) in opp_t else 2), abs(cx - tx) + abs(cy - ty), cy, cx)
            if score < best:
                best = score
                dx, dy = ddx, ddy

    return [int(dx), int(dy)]