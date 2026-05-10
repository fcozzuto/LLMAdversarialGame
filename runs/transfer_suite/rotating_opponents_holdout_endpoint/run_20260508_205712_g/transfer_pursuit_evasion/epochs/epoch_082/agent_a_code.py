def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("hunter" in sr) or ("chaser" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    start = (ox, oy) if is_pursuer else (ox, oy)  # BFS always from opponent position
    if not inb(start[0], start[1]):
        return [0, 0]

    dist = {start: 0}
    q = [start]
    qi = 0
    while qi < len(q):
        x, y = q[qi]
        qi += 1
        nd = dist[(x, y)] + 1
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in dist:
                dist[(nx, ny)] = nd
                q.append((nx, ny))

    best = None
    best_val = None
    # tie-breaker: prefer moves that keep us closer to center (deterministic)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place; simulate deterministically
            dx, dy = 0, 0
        d = dist.get((nx, ny), 10**9)
        val = -d if is_pursuer else d  # pursuer: minimize d; evader: maximize d
        center_pen = abs(nx - cx) + abs(ny - cy)
        val2 = (val, -center_pen) if best_val is None else (val, -center_pen)
        if best is None or val2 > best_val:
            best = (dx, dy)
            best_val = val2

    return [int(best[0]), int(best[1])]