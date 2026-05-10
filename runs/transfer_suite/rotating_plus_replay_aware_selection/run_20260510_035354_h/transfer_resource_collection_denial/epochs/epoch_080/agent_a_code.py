def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(ax, ay, bx, by):
        a = ax - bx
        if a < 0: a = -a
        b = ay - by
        if b < 0: b = -b
        return a + b

    turns_remaining = int(observation.get("turns_remaining", 0) or 0)
    endgame = 1 if turns_remaining and turns_remaining < 6 else 0

    # Pick target deterministically: best race advantage (our dist - opponent dist), then our dist, then coords.
    best = None
    best_key = None
    for rx, ry in res:
        d_self = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        key = (d_self - d_opp, d_self, rx, ry, -endgame)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    candidates = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = None
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Move to reduce our distance; if tied, prefer positions where opponent is further (race), then prefer non-stay.
        score = (d_self, d_self - d_opp, 0 if (dx or dy) else 1, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]