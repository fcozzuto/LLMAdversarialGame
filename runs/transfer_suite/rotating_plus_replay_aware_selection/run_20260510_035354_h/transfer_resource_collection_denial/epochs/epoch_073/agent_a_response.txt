def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if w <= 0 or h <= 0:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Strategic change from baseline: prefer being closer (minimize our distance),
    # only allow contest advantage when we are not clearly behind.
    good = []
    for rx, ry in res:
        sd = md((sx, sy), (rx, ry))
        od = md((ox, oy), (rx, ry))
        if od >= sd:
            good.append((sd, -od, -rx, -ry, rx, ry))
    if good:
        good.sort()
        tx, ty = good[0][4], good[0][5]
    else:
        # If all resources are "behind", take the one where we can catch up best,
        # but still prefer closer-after-adjustment.
        best = None
        for rx, ry in res:
            sd = md((sx, sy), (rx, ry))
            od = md((ox, oy), (rx, ry))
            key = (sd - od, sd, -rx, -ry, rx, ry)
            if best is None or key < best:
                best = key
        tx, ty = best[4], best[5]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nsd = md((nx, ny), (tx, ty))
        nosd = md((ox, oy), (tx, ty))
        # Value: reduce our distance strongly; if equal, prefer moves that
        # keep opponent farther from the same target.
        val = (nsd, nosd - nsd, abs(tx - nx) + abs(ty - ny), -nx, -ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move