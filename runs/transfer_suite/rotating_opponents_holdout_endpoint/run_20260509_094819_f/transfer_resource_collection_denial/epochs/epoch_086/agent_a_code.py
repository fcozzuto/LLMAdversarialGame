def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
                res_set.add((x, y))

    if not res:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick best resource to race for (advantage: opp farther than us).
    best_t = None
    best_adv = None
    for tx, ty in res:
        ds = man(tx, ty, sx, sy)
        do = man(tx, ty, ox, oy)
        adv = (do - ds)  # larger is better
        key = (adv, -ds, -tx, -ty)
        if best_adv is None or key > best_adv:
            best_adv = key
            best_t = (tx, ty)
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        nds = man(nx, ny, tx, ty)
        ndo = man(nx, ny, tx, ty)  # proxy; we also compute from opponent directly below
        opp_ds = man(tx, ty, ox, oy)
        # Immediate gain bonus if landing on a resource.
        gain = 6 if (nx, ny) in res_set else 0
        # Prefer being closer to target; also reduce opponent's race margin after your move.
        my_dist = nds
        opp_dist = opp_ds
        score = (gain, (opp_dist - my_dist), -my_dist, -(dx == 0 and dy == 0))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]