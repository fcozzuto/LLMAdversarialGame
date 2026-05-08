def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    # Evader: run toward corner farthest from pursuer, while reducing immediate risk from being blocked by obstacles.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # Pursuer: target directly at opponent.
        tx, ty = ox, oy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_op = dist2(nx, ny, ox, oy)
        d_tg = dist2(nx, ny, tx, ty)

        # Penalty for moves that get surrounded locally (staying with fewer legal exits is usually worse for evader).
        legal = 0
        for ddx, ddy in moves:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                legal += 1

        # Deterministic evaluation:
        # Evader: maximize distance to opponent first, then prefer being closer to its chosen corner, then more local mobility.
        # Pursuer: minimize distance to opponent first, then prefer moving toward opponent position, then reduce evader mobility.
        if is_evader:
            val = (d_op, -d_tg, legal)
        else:
            val = (-d_op, -d_tg, -legal)

        if best is None or val > best_val:
            best = [dx, dy]
            best_val = val

    if best is None:
        return [0, 0]
    return best