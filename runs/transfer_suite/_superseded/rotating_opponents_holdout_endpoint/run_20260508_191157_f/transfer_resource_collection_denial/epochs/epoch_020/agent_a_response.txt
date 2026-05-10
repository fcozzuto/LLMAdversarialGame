def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we can beat (or at least not lose to) the denier.
    best_r = None
    best_rel = None
    best_my = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        rel = opd - myd  # >0 means we're closer
        if best_rel is None or rel > best_rel or (rel == best_rel and myd < best_my):
            best_rel = rel
            best_my = myd
            best_r = (rx, ry)

    tx, ty = best_r

    # One-step move: maximize our relative advantage after the move, with obstacle penalty.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            score = (-10**9, 0, 0)
        else:
            myd = abs(tx - nx) + abs(ty - ny)
            opd = abs(tx - ox) + abs(ty - oy)
            rel = opd - myd
            # small tie-breaks: prefer reducing distance, and avoid letting opponent get too close overall
            opp_near = min(dist((rx, ry), (ox, oy)) for rx, ry in resources)
            my_near = min(dist((rx, ry), (nx, ny)) for rx, ry in resources)
            score = (rel, -myd, -(opp_near - my_near))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]