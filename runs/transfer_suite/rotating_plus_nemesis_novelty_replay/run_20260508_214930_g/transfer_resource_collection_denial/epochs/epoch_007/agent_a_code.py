def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict) and "x" in p and "y" in p:
            obs.add((int(p["x"]), int(p["y"])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    best = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            rx, ry = int(r["x"]), int(r["y"])
        else:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = od - sd
        tieb = -sd
        if best is None or (val, tieb) > best[0]:
            best = ((val, tieb), rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer approaching target; break ties by distancing from opponent; discourage staying if worse.
        score = (-d_self, d_opp, -(dx == 0 and dy == 0), -(abs(d_self - cheb(sx, sy, tx, ty)) < 0))
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]