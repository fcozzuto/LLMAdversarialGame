def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    res_set = set(resources)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Fallback: minimize opponent advantage by staying closer to center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if (d, nx, ny, dxm) < (best[0], best[1], best[2], best[3]):
                best = (d, nx, ny, dxm)
        return [best[3], best[2] * 0]

    best_val = -10**18
    best_move = [0, 0]

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        if (nx, ny) in res_set:
            val = 10**9
            # slight deterministic preference to moves that also reduce opponent distance
            val += cheb(nx, ny, ox, oy) * -1
        else:
            our_best = -10**18
            for rx, ry in resources:
                ourd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                adv = oppd - ourd  # positive means we are closer than opponent
                score = adv * 1000 - ourd  # heavily prefer winning a resource race
                if score > our_best:
                    our_best = score
            val = our_best
            # discourage moves that give the opponent immediate access
            # (if a neighboring cell is much closer to some resource for opponent than for us, avoid)
            worst_pen = 0
            if resources:
                for rx, ry in resources:
                    d_opp = cheb(ox, oy, rx, ry)
                    d_us = cheb(nx, ny, rx, ry)
                    if d_opp + 0 == d_us:  # tie risk
                        worst_pen -= 5
                        break
            val += worst_pen

        if val > best_val:
            best_val = val
            best_move = [dxm, dym]
    return best_move