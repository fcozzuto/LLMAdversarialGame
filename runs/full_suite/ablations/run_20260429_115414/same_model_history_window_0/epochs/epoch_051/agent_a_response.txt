def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    best_res = None
    best_val = None
    for r in resources:
        rv = (r[0], r[1])
        ds = dist(self_pos, rv)
        do = dist(opp_pos, rv)
        # Prefer resources we can reach earlier; avoid contested close races.
        val = ds + (2 if do < ds else 0) + (0.01 * (ds - do))
        if best_val is None or val < best_val or (val == best_val and (rv[0] + rv[1]) % 2 == observation["turn_index"] % 2):
            best_val = val
            best_res = rv

    tx, ty = best_res
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy, nx, ny in moves:
        dtt = abs(nx - tx) + abs(ny - ty)
        dod = abs(nx - ox) + abs(ny - oy)
        # Smaller distance to target is better; also keep away from opponent slightly.
        score = dtt * 10 - (dod * 0.1)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]