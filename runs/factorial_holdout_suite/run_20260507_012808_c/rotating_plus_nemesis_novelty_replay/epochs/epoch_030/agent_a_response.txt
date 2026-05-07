def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        # Prefer resources where we are closer; break ties deterministically by position.
        # Slight preference to nearer absolute distance for execution.
        score = (myd - opd, myd, rx, ry)
        if best is None or score < best[0]:
            best = (score, rx, ry)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (dx != 0 or dy != 0) and (0 <= nx < w and 0 <= ny < h) and (nx, ny) not in obstacles:
        return [dx, dy]

    # If blocked, try axis moves deterministically, then stay.
    cand = []
    if dx != 0:
        cand.append((dx, 0))
    if dy != 0:
        cand.append((0, dy))
    if dx != 0 and dy != 0:
        cand.append((dx, 0))
        cand.append((0, dy))
    cand.append((0, 0))

    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(mx), int(my)]

    return [0, 0]