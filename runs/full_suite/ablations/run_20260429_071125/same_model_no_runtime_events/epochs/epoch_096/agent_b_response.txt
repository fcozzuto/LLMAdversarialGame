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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = [0, 0]
        bestd = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd:
                bestd = d
                best = [dx, dy]
        return best

    # Strategy: choose a resource to "race" (self_dist smaller than opponent_dist),
    # but also bias to resources the opponent is much closer to (interception/blocking).
    best_res = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer overtaking (od - sd), with a penalty for being far.
        # When opponent is closer, this still can be chosen to block.
        val = (od - sd) * 3 - sd + (od - sd) // 2
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res

    # Move toward target while maximizing separation from opponent as a secondary objective.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd2 = cheb(nx, ny, rx, ry)
        dpos = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to target; Secondary: maximize distance from opponent; Tertiary: deterministic tie.
        candidates.append((sd2, -dpos, dx, dy))

    candidates.sort()
    _, _, dx, dy = candidates[0]
    return [dx, dy]