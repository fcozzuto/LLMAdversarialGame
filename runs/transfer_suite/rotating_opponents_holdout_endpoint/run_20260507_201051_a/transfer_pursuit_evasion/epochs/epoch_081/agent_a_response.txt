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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    best_move = (0, 0)
    best_val = None

    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        dist = abs(nx - ox) + abs(ny - oy)
        if is_pursuer:
            # Prefer decreasing distance; if tied, move toward center.
            center = (w - 1) / 2.0, (h - 1) / 2.0
            center_score = - (abs(nx - center[0]) + abs(ny - center[1]))
            val = (dist, -(abs(nx - sx) + abs(ny - sy)), -center_score)
        else:
            # Prefer increasing distance; if tied, head to farthest corner from pursuer.
            far_corner_from_opp = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_score = - (abs(nx - far_corner_from_opp[0]) + abs(ny - far_corner_from_opp[1]))
            val = (-dist, -(abs(nx - ox) + abs(ny - oy)), corner_score)

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            if is_pursuer:
                if val < best_val:
                    best_val, best_move = val, (dx, dy)
            else:
                if val < best_val:
                    best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]