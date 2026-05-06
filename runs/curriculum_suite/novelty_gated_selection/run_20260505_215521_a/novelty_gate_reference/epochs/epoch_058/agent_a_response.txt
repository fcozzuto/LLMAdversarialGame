def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    us = (sx, sy)
    op = (ox, oy)
    best_own = None
    own_d = 10**9
    best_intercept = None
    best_gap = -10**9

    for rx, ry in resources:
        cell = (rx, ry)
        u = dist(us, cell)
        v = dist(op, cell)
        if u < own_d:
            own_d = u
            best_own = cell
        gap = (u - v)  # positive means we're closer
        if v < u - 1 and (v - u) < (-best_gap):  # prefer where opponent is clearly closer
            pass
        if v < u - 1:
            # Opponent advantage = u - v; bigger means more important to deny
            if (u - v) > best_gap:
                best_gap = u - v
                best_intercept = cell

    target = best_intercept if best_intercept is not None else best_own

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = 10**18
    tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist(op, (tx, ty))
        # If intercepting, prefer reducing opponent ability: bring closer to target and slightly increase distance between agents.
        agent_sep = dist((nx, ny), op)
        score = d_self * 10 - agent_sep + (0 if best_intercept is None else -d_opp)
        if score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]