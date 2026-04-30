def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    if not res:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    def dist(a, b):
        x = a[0] - b[0]
        y = a[1] - b[1]
        if x < 0: x = -x
        if y < 0: y = -y
        return x if x > y else y  # Chebyshev

    rem = observation.get("remaining_resource_count", None)
    late = False
    try:
        late = int(rem) <= 4 if rem is not None else False
    except:
        late = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obs:
            continue
        myd = min(dist((nx, ny), r) for r in res)
        opd = min(dist((ox, oy), r) for r in res)
        opp_term = dist((nx, ny), (ox, oy))
        val = (myd * 10) + (opd * 2)
        if late:
            val -= opp_term  # push more against opponent near the end
        else:
            val += opp_term // 4  # avoid getting too close early
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]
    return [int(best[0]), int(best[1])]