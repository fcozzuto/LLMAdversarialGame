def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res_set = set(tuple(r) for r in resources)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        hit = 1 if (nx, ny) in res_set else 0
        nearest = 10**9
        row_nearest = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
            dr = abs(ny - ry)
            if dr < row_nearest:
                row_nearest = dr

        # Opponent is a sweep-row style; contest the opponent's row primarily.
        strip_dist = abs(ny - oy)
        opp_dist = man(nx, ny, ox, oy)

        # Key: maximize hit, then prefer staying on opponent's row, then reduce distance to resources.
        key = (hit, -strip_dist, -row_nearest, -(nearest + 0.35 * opp_dist), -man(sx, sy, nx, ny), -((nx + ny) & 1))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]