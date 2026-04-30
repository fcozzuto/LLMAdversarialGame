def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    tx, ty = sx, sy
    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer closer to self; break ties by making it farther from opponent; deterministic tie-break by coords
            val = (ds - (do * 0.3), ds, -do, rx, ry)
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (10**9, -10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Minimize distance to target; maximize separation from opponent; deterministic tie-break by dx/dy
        cand = (d_self, -d_opp, abs(tx - nx) + abs(ty - ny), dx, dy)
        if cand < best_move[:5]:
            best_move = (d_self, -d_opp, abs(tx - nx) + abs(ty - ny), dx, dy)

    return [int(best_move[3]), int(best_move[4])]