def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role)

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # obstacle-aware: penalize moves that restrict immediate escape/approach (local dead-ends)
        free_neighbors = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                free_neighbors += 1
        dead_pen = (9 - free_neighbors) * 2

        corner_far = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
        # Deterministic tie-break: prefer diagonal (in order already), then lower dx,dy magnitude
        diag_bonus = 1 if (dx != 0 and dy != 0) else 0

        if is_pursuer:
            val = (-d * 5) + (corner_far * 0.02) + (free_neighbors * 0.5) + diag_bonus - dead_pen
        else:
            val = (d * 5) + (corner_far * 0.03) + (free_neighbors * 0.2) + diag_bonus - dead_pen

        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]