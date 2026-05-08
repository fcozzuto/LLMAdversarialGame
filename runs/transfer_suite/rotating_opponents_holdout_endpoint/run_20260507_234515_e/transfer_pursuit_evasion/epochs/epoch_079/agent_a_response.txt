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
    is_evader = not is_pursuer

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj_obst(x, y):
        a = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in rset:
                    a += 1
        return a

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in rset:
            continue

        d = cheb(nx, ny, ox, oy)
        wall_pen = (1 if nx == 0 else 0) + (1 if nx == w - 1 else 0) + (1 if ny == 0 else 0) + (1 if ny == h - 1 else 0)
        ao = adj_obst(nx, ny)
        move_center = (abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny))  # small prefer staying central

        if is_pursuer:
            score = (-d * 10.0) - ao * 3.0 - wall_pen * 1.5 - move_center * 0.05
        else:
            score = (d * 10.0) - ao * 3.0 - wall_pen * 2.0 - move_center * 0.02

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]