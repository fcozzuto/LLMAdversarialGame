def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    un_cells = observation.get("unclaimed_cells") or []
    if not un_cells:
        target = (ox, oy)
    else:
        target = None
        best = 10**9
        for p in un_cells:
            x, y = p[0], p[1]
            d = abs(sx - x) + abs(sy - y)
            if d < best:
                best = d
                target = (x, y)
        if target is None:
            target = (ox, oy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_to_target = abs(nx - target[0]) + abs(ny - target[1])
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer getting closer to target and (slightly) farther from opponent.
        score = (-dist_to_target) + 0.1 * dist_to_opp
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move