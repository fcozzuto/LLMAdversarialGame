def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbors(x, y):
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if valid(nx, ny):
                    out.append((dx, dy, nx, ny))
        return out

    cands = neighbors(sx, sy)
    if not cands:
        return [0, 0]

    if resources:
        best = None
        best_score = -10**18
        cx = w - 1
        cy = h - 1
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            # prefer resources we can reach first; otherwise still prefer close ones
            score = (dO - dS) * 1000 - dS * 3 - cheb(rx, ry, cx, cy) * 0.01
            if score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # choose move that minimizes distance to target; tie-break by maximizing distance from opponent
    best_move = None
    best_d = 10**9
    best_od = -1
    for dx, dy, nx, ny in cands:
        d = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        if d < best_d or (d == best_d and od > best_od) or (d == best_d and od == best_od and (dx, dy) < best_move):
            best_d = d
            best_od = od
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]