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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_key = None

    for dxm in (-1, 0, 1):
        for dym in (-1, 0, 1):
            nx, ny = sx + dxm, sy + dym
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # One-step lookahead: after moving, choose the best contested resource to target.
            my_best = None
            for tx, ty in resources:
                my_d = cheb(nx, ny, tx, ty)
                opp_d = cheb(ox, oy, tx, ty)
                # Advantage: lower (my_d - opp_d) is better; slight bias to reduce my_d.
                key = (my_d - opp_d, my_d, tx, ty)
                if my_best is None or key < my_best:
                    my_best = key

            # Prefer moves that result in better (my - opp) on the chosen resource.
            if my_best is None:
                continue
            if best_key is None or my_best < best_key:
                best_key = my_best
                best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]