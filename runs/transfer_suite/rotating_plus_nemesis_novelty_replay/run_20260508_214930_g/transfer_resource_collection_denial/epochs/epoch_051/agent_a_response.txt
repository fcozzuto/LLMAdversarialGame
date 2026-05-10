def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def greedy_step(px, py, tx, ty):
        dx = 0
        if tx > px: dx = 1
        elif tx < px: dx = -1
        dy = 0
        if ty > py: dy = 1
        elif ty < py: dy = -1
        nx, ny = px + dx, py + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return nx, ny
        best = (px, py)
        bestd = cheb(px, py, tx, ty)
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                if mx == 0 and my == 0:
                    continue
                nx, ny = px + mx, py + my
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    d = cheb(nx, ny, tx, ty)
                    if d < bestd or (d == bestd and (nx, ny) < best):
                        bestd = d
                        best = (nx, ny)
        return best

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = None

    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            val = -10**9
        else:
            val = -10**9
            for tx, ty in res:
                self_nd = cheb(nx, ny, tx, ty)
                gnx, gny = greedy_step(ox, oy, tx, ty)
                opp_nd = cheb(gnx, gny, tx, ty)
                score = (opp_nd - self_nd) * 10 - self_nd
                if score > val:
                    val = score
        if best_val is None or val > best_val or (val == best_val and (mx, my) < best_move):
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]