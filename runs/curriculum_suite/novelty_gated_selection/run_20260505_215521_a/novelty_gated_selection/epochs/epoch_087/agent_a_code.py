def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        best = (10**9, -10**9, 0, 0)  # (score, safety, dx, dy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(nx, ny, ox, oy)
            # Higher safety is better; lower self_d is better; slight preference for shorter overall progress.
            score = self_d * 10 + (cheb(ox, oy, tx, ty) - opp_d)
            safety = opp_d
            if (score, -safety) < (best[0], -best[1]):
                best = (score, safety, dx, dy)
        if best[2] == 0 and best[3] == 0:
            return [0, 0]
        return [best[2], best[3]]

    if not resources:
        # Deterministic "edge_patrol" defense: move to maximize distance from opponent while not colliding.
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_resource = None
    best_val = 10**18
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Value: prioritize resources we can reach sooner than opponent; also slightly prefer central-ish.
        central = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        val = (d_self - 0.9 * d_opp) * 100 + central
        if val < best_val:
            best_val = val
            best_resource = (rx, ry)

    tx, ty = best_resource
    return step_toward(tx, ty)