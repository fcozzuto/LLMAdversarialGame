def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        resources.sort()
        cx, cy = w // 2, h // 2
        best_t = (cx, cy)
        best_v = 10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            lead = d_op - d_me  # positive if we can reach first (or tie advantage)
            # Prefer reachable-first resources; otherwise block by lowering opponent advantage.
            v = 0
            if lead > 0:
                v = d_me - 1.5 * lead
            elif lead == 0:
                v = d_me + 0.25
            else:
                v = (d_me + 0.7 * (-lead)) + 0.05 * cheb(rx, ry, cx, cy)
            # Deterministic tie-break closer to center after primary scoring
            if v < best_v - 1e-12 or (abs(v - best_v) <= 1e-12 and (rx, ry) < best_t):
                best_v = v
                best_t = (rx, ry)
        tx, ty = best_t

    # Greedy one-step toward chosen target; if blocked, steer toward next-best neighbor by local eval.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        # Small anti-opponent pressure: don't walk into being worse at the same target
        d1op = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; slightly prefer increasing distance from opponent
        score = d1 - 0.02 * d1op
        candidates.append((score, nx, ny))
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, nx, ny = candidates[0]
    return [nx - sx, ny - sy]