def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(r) for r in (observation.get("resources") or []) if 0 <= r[0] < w and 0 <= r[1] < h and tuple(r) not in obstacles]
    ox, oy = observation["opponent_position"]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        tx = 1 if sx < cx else -1 if sx > cx else 0
        ty = 1 if sy < cy else -1 if sy > cy else 0
        return [int(tx), int(ty)]

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = -10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        center_bias = -0.001 * d2(nx, ny, cx, cy)
        move_score = center_bias

        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                val = 10**9
            else:
                # Prefer resources I'm closer to; if not, still prefer to move toward cells far from opponent.
                val = (opd - myd) + 0.15 * (opd) - 0.05 * (myd)
            if val > move_score:
                move_score = val

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]