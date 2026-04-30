def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = w - 1 if sx < ox else 0
        ty = h - 1 if sy < oy else 0
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best_t = None
    best_s = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        rel = do - ds  # positive means we are closer
        s = rel * 100 - ds  # prioritize resources where we have advantage
        if best_s is None or s > best_s or (s == best_s and (ds < cheb(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_s = s
            best_t = (rx, ry)

    tx, ty = best_t
    best_m = (0, 0)
    best_ms = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_nt = cheb(nx, ny, tx, ty)
        d_no = cheb(nx, ny, ox, oy)
        # Go toward target, keep away from opponent to reduce their contest chance
        ms = -d_nt * 100 + d_no - cheb(nx, ny, tx, ty)  # deterministic tie-break weight
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_m = (mx, my)

    mx, my = best_m
    if not (isinstance(mx, int) and isinstance(my, int)):
        return [0, 0]
    return [mx, my]