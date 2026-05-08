def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    i_am_evader = not any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx >= dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                d = cheb(nx, ny)
                # Prefer staying if it doesn't worsen (deterministic tie-break via order)
                cand.append((d, -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2), dx, dy))

    if not cand:
        return [0, 0]

    # Evader: maximize distance; Pursuer: minimize distance
    if i_am_evader:
        best = max(cand, key=lambda t: (t[0], t[1], -t[2], -t[3]))
    else:
        best = min(cand, key=lambda t: (t[0], t[1], t[2], t[3]))

    return [best[2], best[3]]