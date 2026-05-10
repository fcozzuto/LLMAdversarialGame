def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None

    # Prefer corner control for evader; for pursuer, prefer squeezing distance.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    cx, cy = best_corner

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Secondary: how it changes relative to corner (evader) or cuts off (pursuer).
        if evader:
            sec = abs(nx - cx) + abs(ny - cy)
            score = (dist, sec, -abs(dx) - abs(dy))
        else:
            # Pursuer wants smaller distance and to move toward the line between agents:
            # use corner farthest from evader as a proxy "target" to force turns.
            far_corner = max(corners, key=lambda c: abs(c[0] - nx) + abs(c[1] - ny))
            fx, fy = far_corner
            sec = -(abs(nx - fx) + abs(ny - fy))
            score = (-dist, sec, -abs(dx) - abs(dy))

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]