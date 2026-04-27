def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def dist(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    # Pick a target resource based on how much faster we reach it than the opponent.
    if resources:
        best = None
        for r in resources:
            tx, ty = r[0], r[1]
            if not in_bounds(tx, ty) or (tx, ty) in obstacles:
                continue
            sd = dist((sx, sy), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            adv = od - sd
            key = (adv, -sd, tx, ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        target = best[1] if best is not None else resources[0]
    else:
        # No resources left: move towards opponent to contest space deterministically.
        target = (ox, oy)
    tx, ty = target
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    cur_d = dist((sx, sy), (tx, ty))
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # Primary: minimize distance to target; Secondary: maximize progress; Tertiary: deterministic ordering.
        score = (-(nd), nd - cur_d, -abs((nx - tx)) - abs((ny - ty)), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]