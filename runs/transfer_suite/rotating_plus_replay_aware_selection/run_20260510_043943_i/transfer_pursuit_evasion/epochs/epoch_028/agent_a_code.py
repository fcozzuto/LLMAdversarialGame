def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    pursuer = any(k in self_role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit")) or ("evader" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x, y):
        return abs(x - ox) + abs(y - oy)

    def obstacle_touches(x, y):
        # count blocked neighbors (encourages not getting "pinched")
        c = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                c += 1
        return c

    # deterministic tie-break prefers moves earlier in list
    best_move = [0, 0]
    best_val = None

    # For evader, also prefer direction toward the farthest corner from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = manh(nx, ny)
        pinch = obstacle_touches(nx, ny)

        if pursuer:
            # chase strongly; avoid pinch slightly
            val = (d, pinch, -abs(dx) - abs(dy))
            # minimize lexicographically
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # evade strongly; avoid pinch; also drift to far corner
            drift = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
            val = (-d, -drift, pinch, -abs(dx) - abs(dy))
            # minimize lexicographically on this tuple
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]