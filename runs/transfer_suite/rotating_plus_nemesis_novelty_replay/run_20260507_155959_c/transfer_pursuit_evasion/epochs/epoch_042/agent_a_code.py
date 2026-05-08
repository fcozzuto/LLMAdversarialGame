def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")
    my_is_pursuer = is_pursuer

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(px, py, dx, dy):
        nx, ny = px + dx, py + dy
        return (nx, ny) if valid(nx, ny) else (px, py)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: man(c, (ox, oy)))

    best_move = (0, 0)
    best_score = None

    for dx, dy in cand:
        nx, ny = step(sx, sy, dx, dy)
        d = man((nx, ny), (ox, oy))
        if my_is_pursuer:
            # chase while prefer diagonal progress; penalize obstacle-adjacent squares
            score = (-d * 100) + (-(abs(nx - ox) + abs(ny - oy)) * 2) + (-(adj_obst(nx, ny)) * 3)
            better = best_score is None or score > best_score
        else:
            # evader: maximize separation; bias toward farthest corner; avoid obstacle traps
            corner_bias = -man((nx, ny), best_corner)
            score = (d * 100) + (corner_bias * 2) - (adj_obst(nx, ny) * 5)
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]