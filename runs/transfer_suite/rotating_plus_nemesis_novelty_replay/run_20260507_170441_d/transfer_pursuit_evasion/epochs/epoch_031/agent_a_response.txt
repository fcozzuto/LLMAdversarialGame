def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Evader_corner heuristic: assume opponent aims for the corner farthest from us.
    target_corner = max(corners, key=lambda c: man(sx, sy, c[0], c[1]))
    cx, cy = target_corner

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, cx, cy)

        # Interception bias: get closer to the evasion corner while still pressuring.
        tx = 0 if cx == ox else (1 if cx > ox else -1)
        ty = 0 if cy == oy else (1 if cy > oy else -1)
        align = (nx - ox) * tx + (ny - oy) * ty  # positive means "in front" of opponent toward corner

        score = 2 * d_opp + d_corner - 0.25 * align

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]