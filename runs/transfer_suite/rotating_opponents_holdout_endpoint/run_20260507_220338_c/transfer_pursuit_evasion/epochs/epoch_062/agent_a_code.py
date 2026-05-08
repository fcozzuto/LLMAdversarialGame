def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = any(k in role_s for k in ("evader", "runner", "flee", "fleeing", "evade", "avoid"))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                m += 1
        return m

    def corner_bias(x, y):
        # Encourage corners only when evading (more deterministic than chasing corners blindly)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max((abs(cx - x) + abs(cy - y) for cx, cy in corners), default=0)

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            # If invalid, the engine keeps us in place; score accordingly by treating as (sx,sy)
            nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        if is_evader:
            # Maximize distance; also prefer staying mobile; slight preference for moving toward farthest corner
            score = (d * 10.0) + (mob * 1.0) + (corner_bias(nx, ny) * 0.02)
        else:
            # Pursuer: minimize distance; prefer moves that improve mobility and avoid being boxed by obstacles
            score = (-d * 10.0) + (mob * 1.0)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best