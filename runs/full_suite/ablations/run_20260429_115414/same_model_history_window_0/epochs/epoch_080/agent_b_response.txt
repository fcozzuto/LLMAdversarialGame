def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w - 1, h - 1) if (observation["turn_index"] % 2 == 0) else (0, 0)
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                sc = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if sc < best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]]

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    t = observation["turn_index"]
    if t % 2 == 0:
        target = min(resources, key=lambda r: d2(sx, sy, r[0], r[1]))
    else:
        target = max(resources, key=lambda r: (d2(ox, oy, r[0], r[1]) - d2(sx, sy, r[0], r[1])))

    tx, ty = target[0], target[1]
    best_score = 10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_self = d2(nx, ny, tx, ty)
        dist_opp = d2(nx, ny, ox, oy)
        # When racing (odd turns), prefer moves that also pull away from opponent.
        race_penalty = 0
        if t % 2 == 1:
            race_penalty = -0.03 * dist_opp
        score = dist_self + race_penalty
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]