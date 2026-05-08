def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("seeker" in role) or ("pursuer" in role)

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pressure(x, y):
        c = 0
        for dx, dy in neigh8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    best = None
    best_val = None
    dx0 = dy0 = 0
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        p = obstacle_pressure(nx, ny)
        if is_pursuer:
            # Minimize distance to evader; prefer moves with less obstacle pressure.
            val = (d, p, dx, dy)
        else:
            # Maximize distance from pursuer; prefer safer cells (lower obstacle pressure).
            val = (-d, p, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    if best is None:
        return [0, 0]
    dx, dy = best
    return [int(dx), int(dy)]