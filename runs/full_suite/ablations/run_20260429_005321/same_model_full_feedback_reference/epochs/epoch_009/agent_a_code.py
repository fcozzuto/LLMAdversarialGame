def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if resources:
        best_t = resources[0]
        best_val = -10**18
        for r in resources:
            myd = md(me, r)
            opd = md(opp, r)
            val = (opd - myd) * 10.0 - myd * 1.0
            # Small deterministic tie-breaker
            val -= (r[0] * 0.001 + r[1] * 0.00001)
            if val > best_val:
                best_val = val
                best_t = r
        target = best_t

        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            nd_my = md((nx, ny), target)
            nd_opp = md((nx, ny), opp)
            score = -nd_my * 2.0 + nd_opp * 0.15
            if nd_my == 0:
                score += 1000.0
            # Tie-break: prefer moves that reduce both x then y deterministically
            score -= (dx * 0.0001 + dy * 0.00001)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources left: head to the corner farthest from opponent
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corners[0]
    best_d = -1
    for c in corners:
        d = md(c, opp)
        if d > best_d:
            best_d = d
            best_corner = c
    tx, ty = best_corner

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = -md((nx, ny), (tx, ty)) - 0.05 * md((nx, ny), opp)
        score -= (dx * 0.0001 + dy * 0.00001)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]