def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs.add((int(p["x"]), int(p["y"])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))

    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_global = None
    for tx, ty in res:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # prefer resources I can arrive to first; tie-break by closer
        score = (od - md) * 1000 - md
        if best_global is None or score > best_global[0]:
            best_global = (score, tx, ty, md, od)
    _, target_x, target_y, _, _ = best_global

    # local evaluation for immediate/next step competitiveness
    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        if (nx, ny) in obs:
            return -10**9
        immediate = 1 if (nx, ny) == (target_x, target_y) else 0

        # if we overshoot, reduce score; also avoid walking into opponent-faster alternative
        best_alt = -10**9
        for tx, ty in res:
            if tx == nx and ty == ny:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            s = (opd - myd) * 1000 - myd
            if s > best_alt:
                best_alt = s
        # choose move that keeps me closest to current target while denying opponent
        md = cheb(nx, ny, target_x, target_y)
        od = cheb(ox, oy, target_x, target_y)
        deny = (od - md) * 200
        return immediate * 10**6 - md * 50 + best_alt * 0.01 + deny

    best = None
    for dx, dy in moves:
        v = eval_move(dx, dy)
        if best is None or v > best[0]:
            best = (v, dx, dy)
    return [best[1], best[2]]