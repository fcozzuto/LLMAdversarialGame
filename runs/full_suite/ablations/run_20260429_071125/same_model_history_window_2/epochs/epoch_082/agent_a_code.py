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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (None, -10**18, 0, 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obst:
            continue

        my_adv = -10**18
        best_res = None
        for tx, ty in res:
            md = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer resources where we can create capture advantage now; also avoid ones opponent is already much closer to.
            adv = (od - md)
            if md == 0:
                adv += 3  # immediate grab priority
            if (adv > my_adv) or (adv == my_adv and (tx, ty) < (best_res[0], best_res[1]) if best_res else True):
                my_adv = adv
                best_res = (tx, ty)

        # Secondary tie-break: steer toward the chosen target, then toward center, deterministically.
        tx, ty = best_res
        dist_to_target = cheb(nx, ny, tx, ty)
        center_bias = abs(nx - cx) + abs(ny - cy)
        score = (my_adv, -dist_to_target, -center_bias, -dx, -dy)
        if best[0] is None or score > (best[1], best[2], best[3], best[0][0], best[0][1]):
            best = ((dx, dy), score[0], score[1], score[2])

    return [int(best[0][0]), int(best[0][1])]