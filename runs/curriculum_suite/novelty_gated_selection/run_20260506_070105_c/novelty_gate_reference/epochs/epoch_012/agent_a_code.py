def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2 and inb(r[0], r[1]):
            res.append((r[0], r[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not res:
        cx, cy = w // 2, h // 2
        tx, ty = cx - sx, cy - sy
        return [0 if tx == 0 else (1 if tx > 0 else -1), 0 if ty == 0 else (1 if ty > 0 else -1)]

    resset = set(res)

    # Immediate capture
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in resset:
            return [dx, dy]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def nearest_dist(x, y):
        best = 10**9
        for rx, ry in res:
            d = md(x, y, rx, ry)
            if d < best:
                best = d
        return best

    # Opponent assumed greedy toward its nearest resource
    opp_best_next = (ox, oy)
    opp_best_d = nearest_dist(ox, oy)
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny):
            d = nearest_dist(nx, ny)
            if d < opp_best_d:
                opp_best_d = d
                opp_best_next = (nx, ny)

    center = (w // 2, h // 2)
    opx, opy = opp_best_next
    op_term = -nearest_dist(opx, opy)

    # Evaluate our moves with deterministic tie-breaking
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = nearest_dist(nx, ny)
        # Encourage moving toward resources and away from letting opponent get relatively closer
        score = (-my_d) + (0.35 * (-op_term)) + (-0.02 * md(nx, ny, center[0], center[1]))
        # Slightly prefer moves that reduce distance to currently best resource for interception
        best_r = min(res, key=lambda t: md(sx, sy, t[0], t[1]))
        score += -0.01 * md(nx, ny, best_r[0], best_r[1])
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move