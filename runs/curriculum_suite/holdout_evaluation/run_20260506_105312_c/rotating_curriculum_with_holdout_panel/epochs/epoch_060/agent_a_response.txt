def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def manh(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources where we have an advantage; tie-break by closer absolute distance.
        best_r = None
        best_key = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            our_d = manh(sx, sy, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            # maximize (opp_d - our_d), then minimize our_d, then lexicographic cell
            key = (opp_d - our_d, -our_d, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r

    # Choose next step: valid move that most reduces our distance to target,
    # while still keeping/increasing our advantage vs opponent.
    best = None
    best_pair = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_d1 = manh(nx, ny, tx, ty)
        opp_d = manh(ox, oy, tx, ty)
        adv1 = opp_d - our_d1
        pair = (adv1, -our_d1, dx, dy)
        if best_pair is None or pair > best_pair:
            best_pair = pair
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best else [0, 0]