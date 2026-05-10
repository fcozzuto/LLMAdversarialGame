def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for it in observation.get("obstacles", []) or []:
        if it is None:
            continue
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        if x is None or y is None:
            continue
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))  # farthest corner from pursuer

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist_cheb(x1, y1, x2, y2):
        a = abs(x1 - x2)
        b = abs(y1 - y2)
        return a if a >= b else b

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist_cheb(nx, ny, ox, oy)
        if i_am_pursuer:
            # minimize distance; prefer moving roughly toward opponent (secondary)
            score = (d, abs(nx - ox) + abs(ny - oy), -abs(nx - target_corner[0]) - abs(ny - target_corner[1]))
            # also strongly prefer capture-closer moves
            score = (d, abs(nx - ox) + abs(ny - oy))
            if best is None or score < best_score:
                best, best_score = (dx, dy), score
        else:
            # maximize distance; prefer staying near target corner while avoiding obstacles
            to_corner = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
            score = (-d, to_corner, abs(nx - ox) + abs(ny - oy))
            if best is None or score < best_score:
                best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]