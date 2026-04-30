def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    moves = [m for m in moves if m[0] in (-1, 0, 1) and m[1] in (-1, 0, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy
    if not resources:
        target = (w // 2, h // 2)
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            v = d2(nx, ny, target[0], target[1])
            if bestv is None or v < bestv or (v == bestv and [dx, dy] < best):
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        worst_penalty = 0
        for rx, ry in resources:
            self_d = d2(nx, ny, rx, ry)
            opp_d = d2(ox, oy, rx, ry)
            # Favor targets where we can reduce opponent's advantage (opp_d - self_d).
            # Also slightly prefer closer targets for faster capture.
            val = (opp_d - self_d) * 10 - self_d
            # Penalize moving far from us compared to staying, to avoid dithering.
            val -= d2(nx, ny, sx, sy) * 0.2
            if best_val is None or val > best_val or (val == best_val and [dx, dy] < best_move):
                best_val = val
                best_move = [dx, dy]
    return best_move if best_val is not None else [0, 0]