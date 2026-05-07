def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Race for resources: maximize (opponent_dist - self_dist), then prefer earliest/central/right-biased tie-break.
    center_bias_x = (sx - (w - 1) / 2.0)
    center_bias_y = (sy - (h - 1) / 2.0)
    best_t = None
    best_key = None
    for tx, ty in resources:
        myd = dist(sx, sy, tx, ty)
        opd = dist(ox, oy, tx, ty)
        lead = opd - myd  # positive means we arrive first/sooner
        # Encourage picking resources that remain reachable within time.
        tr = int(observation.get("turns_remaining") or 0)
        time_ok = 1 if myd <= tr else 0
        key = (lead, time_ok, -myd, -(tx + 0.01 * ty), abs(center_bias_x) + abs(center_bias_y))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = [0, 0]
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = dist(nx, ny, tx, ty)
        # Prefer moves that improve lead against opponent for that same target.
        opd2 = dist(ox, oy, tx, ty)
        mkey = (opd2 - myd2, -myd2, -dx, -dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]
    return best_move