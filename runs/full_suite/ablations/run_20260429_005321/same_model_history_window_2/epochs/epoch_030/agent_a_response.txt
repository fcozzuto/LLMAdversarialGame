def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_prox_pen = cheb(nx, ny, ox, oy)
        if resources:
            best_adv = -10**9
            best_ds = 10**9
            best_tie = 0
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                adv = do - ds  # positive if we are closer than opponent (using their current position)
                # encourage taking resources on "useful" parity relative to turn to reduce dithering
                parity = (int(observation.get("turn_index", 0) or 0) + rx + ry) & 1
                cand = (adv, -ds, -parity)
                if cand > (best_adv, -best_ds, best_tie):
                    best_adv = adv
                    best_ds = ds
                    best_tie = parity
            score = (best_adv, -best_ds, -opp_prox_pen, -((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy)))
        else:
            # no visible resources: move to increase distance from opponent while heading toward center
            score = (-opp_prox_pen, -((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy)), 0)

        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]