def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = observation.get("self_role") or "pursuer"
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                cnt += 1
        return cnt

    def score_move(nx, ny):
        d = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        if role == "pursuer":
            # Prefer getting closer, keep options open, avoid "cornering" yourself if blocked.
            return (-d * 10) + mob * 2 + (0.5 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0)
        else:
            # Evader: run away and prefer walls/edges (wall-run), but don't walk into dead-ends.
            edge_bonus = 0
            if nx == 0 or nx == w - 1:
                edge_bonus += 1.5
            if ny == 0 or ny == h - 1:
                edge_bonus += 1.5
            # Also bias toward the farthest corner to maintain consistent direction.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
            tc = dist2(nx, ny, target[0], target[1])
            return (d * 10) + mob * 2 + edge_bonus * 3 - tc * 0.02

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_move(nx, ny)
        if best is None or sc > best_score or (sc == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = sc

    return list(best if best is not None else (0, 0))