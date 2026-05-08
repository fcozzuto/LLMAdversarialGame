def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    rset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                rset.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def obstacle_adjacency(nx, ny):
        # penalize getting close to walls/obstacles
        adj = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                tx, ty = nx + ddx, ny + ddy
                if (tx, ty) in rset:
                    adj += 1
        return adj

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in rset

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        adj_pen = obstacle_adjacency(nx, ny)

        # Pursuer: minimize distance, but avoid obstacles. Evader: maximize distance, avoid obstacles.
        if is_pursuer:
            val = (-d * 100) - adj_pen
        else:
            val = (d * 100) - adj_pen

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]