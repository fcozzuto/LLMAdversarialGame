def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    remaining = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    opp_bias = 1 if remaining <= 4 else 2

    # Pick best resource by "time advantage" (closer for us than opponent).
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        advantage = opp_d - my_d  # positive means we are closer/equal.
        # Deterministic tie-breaks.
        key = (-(advantage), my_d, opp_d, ry, rx, advantage * opp_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_to = cheb(nx, ny, tx, ty)
        # Secondary: prefer moves that also get us closer to the nearest other resource to avoid stalemates.
        nearest2 = 0
        for rx, ry in resources:
            if rx == tx and ry == ty:
                continue
            d = cheb(nx, ny, rx, ry)
            if nearest2 == 0 or d < nearest2:
                nearest2 = d
        nearest2 = nearest2 if nearest2 else 0
        # Slight preference for reducing opponent's chance on the target by moving when we still lead.
        opp_to = cheb(ox, oy, tx, ty)
        lead = cheb(sx, sy, tx, ty) - opp_to
        score = (my_to, nearest2, -lead, abs(nx - ox) + abs(ny - oy), ny, nx)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]