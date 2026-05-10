def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs_set = {(x, y) for x, y in obstacles}
    unclaimed = observation.get("unclaimed_cells", []) or []

    options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    if unclaimed:
        targets = unclaimed
        tx, ty = min(targets, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    best_key = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        hit_unclaimed = (nx, ny) in obs_set  # always False; keep simple deterministic scoring
        k = (-1 if hit_unclaimed else 0, dist, nx, ny, dx, dy)
        if best is None or k < best_key:
            best, best_key = (dx, dy), k

    if best is None:
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]