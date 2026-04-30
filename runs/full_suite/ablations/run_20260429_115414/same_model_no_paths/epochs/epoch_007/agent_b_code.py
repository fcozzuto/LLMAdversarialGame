def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def occ_pen(x, y):
        if not obstacles:
            return 0
        best = 999
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        if best >= 3:
            return 0
        return 6 - best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((nx, ny, dx, dy))
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_score = None
    best_move = (0, 0)

    for nx, ny, dx, dy in legal:
        my_to_center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        pen = occ_pen(nx, ny)
        s = 0
        local_best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier; keep progress toward them.
            score = (opp_d - my_d) * 12 - my_d * 2 + (1 if my_d == 0 else 0)
            # Also discourage stepping into losing races where opponent is much closer.
            score -= max(0, my_d - opp_d) * 3
            if score > local_best:
                local_best = score
        if local_best <= -10**8:
            s = my_to_center - pen
        else:
            s = local_best + my_to_center * 0.01 - pen * 1.5
        # Deterministic tie-break: lower distance to opponent, then lexicographic move
        if best_score is None or s > best_score:
            best_score = s
            best_move = (dx, dy)
        elif s == best_score:
            if cheb(nx, ny, ox, oy) < cheb(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = (dx, dy)
            elif cheb(nx, ny, ox, oy) == cheb(sx + best_move[0], sy + best_move[1], ox, oy):
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]