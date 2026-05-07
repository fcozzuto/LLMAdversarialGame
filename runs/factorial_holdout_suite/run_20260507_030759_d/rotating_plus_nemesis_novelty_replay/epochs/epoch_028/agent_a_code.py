def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    def steps(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev for 8-dir movement

    if not resources:
        return [0, 0]

    avail = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                avail.append((rx, ry))
    if not avail:
        return [0, 0]

    opp_threat = []
    for (rx, ry) in avail:
        od = steps((ox, oy), (rx, ry))
        if od <= 1:
            sd = steps((sx, sy), (rx, ry))
            opp_threat.append(((sd, od), (rx, ry)))
    if opp_threat:
        opp_threat.sort(key=lambda x: (x[0][0], x[0][1], x[1][0], x[1][1]))
        tx, ty = opp_threat[0][1]
    else:
        best = None
        for (rx, ry) in avail:
            sd = steps((sx, sy), (rx, ry))
            od = steps((ox, oy), (rx, ry))
            adv = od - sd
            key = (adv, -sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If staying would be invalidated by obstacles, try an alternate toward target.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
        # Prefer axis moves, then stay.
        cand = []
        if 0 <= sx + dx < w and (sx + dx, sy) not in obstacles:
            cand.append((dx, 0))
        if 0 <= sy + dy < h and (sx, sy + dy) not in obstacles:
            cand.append((0, dy))
        if dx != 0 and dy != 0 and 0 <= sx + dx < w and 0 <= sy + dy < h and (sx + dx, sy) not in obstacles and (sx, sy + dy) not in obstacles:
            pass
        if 0 <= sx < w and 0 <= sy < h:
            cand.append((0, 0))
        dx, dy = cand[0]

    return [int(dx), int(dy)]