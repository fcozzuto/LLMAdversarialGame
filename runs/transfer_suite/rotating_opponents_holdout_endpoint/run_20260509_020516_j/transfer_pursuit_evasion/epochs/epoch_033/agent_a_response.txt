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
    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursue" in self_role)
    i_am_pursuer = pursuer

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer deterministic order by listing moves; break ties by lexicographic move.
    best_move = [0, 0]
    best_val = -10**18 if i_am_pursuer else 10**18

    # Slightly bias to keep mobile: prefer moves that change position when not losing.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)
        # If pursuer: minimize distance. If evader: maximize distance.
        # Add obstacle crowding penalty (avoid stepping near obstacles) and add "escape direction" bias for evader.
        crowd = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    crowd += 1
        if i_am_pursuer:
            val = (-dist * 1000) - crowd * 3 - (0 if (dx == 0 and dy == 0) else 0)
            # If move would capture immediately, dist==0; prioritize strongly.
            val += 100000 if dist == 0 else 0
            if val > best_val:
                best_val, best_move = val, [dx, dy]
        else:
            # Evader: increase distance and also favor moving toward the opposite corner from pursuer.
            corner_bias_x = 7 if ox <= 3 else 0
            corner_bias_y = 7 if oy <= 3 else 0
            corner_dist = cheb(nx, ny, corner_bias_x, corner_bias_y)
            val = (dist * 1000) - crowd * 3 + corner_dist * 2 - (0 if (dx == 0 and dy == 0) else 0)
            if val < best_val:
                best_val, best_move = val, [dx, dy]

    # If all moves invalid, stay still deterministically.
    return [int(best_move[0]), int(best_move[1])]