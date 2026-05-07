def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = p[0], p[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r[0], r[1]
            x, y = int(x), int(y)
            if inside(x, y):
                res.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_dx, best_dy = 0, 0
    best_score = -10**18

    target = None
    if res:
        # Choose nearest resource (tie -> smaller distance, then closer to self tie-break by dx,dy order)
        cur = (sx, sy)
        best_d = None
        for t in res:
            d = dist(cur, t)
            if best_d is None or d < best_d:
                best_d = d
                target = t
    else:
        # No resources: move to reduce distance to opponent
        target = (ox, oy)

    cur = (sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nxt = (nx, ny)
        # Score: prefer shorter distance to target; small penalty for being closer to opponent (encourages territorial play)
        s = -dist(nxt, target) - 0.1 * dist(nxt, (ox, oy))
        if res:
            # If targeting resource, also reward if we are closer than opponent would be next step (very light deterministic pressure)
            s += 0.05 * (dist((ox, oy), target) - dist(nxt, target))
        if s > best_score:
            best_score = s
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]