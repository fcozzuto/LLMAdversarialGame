def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Target selection: prefer resources I'm at least as close to; otherwise attempt a steal.
    tx = ty = None
    if resources:
        candidates = []
        for x, y in resources:
            md = cheb(sx, sy, x, y)
            od = cheb(ox, oy, x, y)
            if md <= od:
                # get it first; tie-break toward smaller md, then more "ahead" vs opponent
                candidates.append((1, md, od - md, x, y))
            else:
                # steal potential
                candidates.append((0, -(od - md), md, x, y))
        # Pick among the two groups with a deterministic key
        best = min(candidates, key=lambda t: (t[0] == 0, t[1], -t[2], t[3], t[4]))
        tx, ty = best[3], best[4]

    # If no resources: chase a deterministic midpoint-ish to stay useful.
    if tx is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, nx, ny)
        to_opp = cheb(nx, ny, ox, oy)
        # Heuristic: reduce distance to target, and avoid getting too close to opponent.
        val = (-my_d * 10) + (-to_opp * 1) + (opp_d * 0.1)
        # Prefer not to stay if movement helps
        if (dx, dy) != (0, 0) and my_d < cheb(sx, sy, tx, ty):
            val += 2
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]