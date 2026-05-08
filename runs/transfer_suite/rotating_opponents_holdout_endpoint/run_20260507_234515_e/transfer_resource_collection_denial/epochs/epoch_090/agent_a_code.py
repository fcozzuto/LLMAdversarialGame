def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestv = [0, 0], -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) + 0.1 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    res_set = {(int(r[0]), int(r[1])) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2}
    best_move, best_val = [0, 0], -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_for_move = -10**18
        for rx, ry in res_set:
            ourd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            lead = oppd - ourd
            v = lead * 10 - ourd
            if (nx, ny) == (rx, ry):
                v += 1000
            # small tie-break to prefer staying away from opponent when unsure
            v += -0.05 * cheb(nx, ny, ox, oy)
            if v > best_for_move:
                best_for_move = v

        if best_for_move > best_val:
            best_val = best_for_move
            best_move = [dx, dy]
    return best_move