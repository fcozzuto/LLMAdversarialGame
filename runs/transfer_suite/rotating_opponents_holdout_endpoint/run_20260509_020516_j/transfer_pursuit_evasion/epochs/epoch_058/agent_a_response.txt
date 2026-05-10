def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-break: prefer diagonal/stable ordering
    moves.sort(key=lambda t: (abs(t[0]) + abs(t[1]), t[0], t[1]))

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)

        # Additional shaping toward/away from opponent while avoiding cornering against walls
        wall_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            wall_pen = 1

        # Prefer moves that keep options: count free neighboring cells
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if in_bounds(tx, ty):
                free += 1

        if "evader" in role:
            score = d * 10 + free - wall_pen * 3
        else:
            score = -d * 10 + free - wall_pen * 3

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]