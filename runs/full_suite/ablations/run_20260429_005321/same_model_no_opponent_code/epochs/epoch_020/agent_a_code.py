def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_score(cx, cy, tx, ty):
        d1 = cheb(cx, cy, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        return d2 - d1  # prefer resources where we are relatively closer

    target = None
    if resources:
        bestv = -10**9
        bestt = None
        for rx, ry in resources:
            v = cell_score(sx, sy, rx, ry)
            if v > bestv or (v == bestv and (rx < bestt[0] or (rx == bestt[0] and ry < bestt[1]))):
                bestv = v
                bestt = (rx, ry)
        target = bestt

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if target is None:
            # fallback: go toward center while staying away from opponent
            tcx, tcy = (w - 1) // 2, (h - 1) // 2
            d_self = cheb(nx, ny, tcx, tcy)
            d_opp = cheb(nx, ny, ox, oy)
            val = -d_self - 0.2 * d_opp
        else:
            tx, ty = target
            d_self_now = cheb(sx, sy, tx, ty)
            d_self_new = cheb(nx, ny, tx, ty)
            d_opp_now = cheb(ox, oy, tx, ty)
            # opponent next move (assume best-effort to reduce distance deterministically by cheb greedy)
            opp_best = cheb(ox, oy, tx, ty)
            for odx, ody in moves:
                mx, my = ox + odx, oy + ody
                if inb(mx, my) and (mx, my) not in obstacles:
                    opp_best = min(opp_best, cheb(mx, my, tx, ty))
            d_opp_new = opp_best

            gained = (d_self_now - d_self_new)
            denied = (d_opp_now - d_opp_new)
            capture_bonus = 0.0
            if (nx, ny) == target:
                capture_bonus = 1000.0
            val = 10.0 * gained + 6.0 * (-denied) + capture_bonus

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]