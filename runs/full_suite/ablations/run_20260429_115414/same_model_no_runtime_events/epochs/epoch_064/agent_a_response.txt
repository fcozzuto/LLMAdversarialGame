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
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                if (x, y) not in res_set:
                    res_set.add((x, y))
                    resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None

    # Strategic change: evaluate moves by taking resources and denying opponent by "distance advantage"
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        captured = 1 if (nx, ny) in res_set else 0
        if resources:
            my_best = None
            opp_best = None
            my_adv_sum = 0
            my_min = 10**9
            for rx, ry in resources:
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                if d_my < my_min:
                    my_min = d_my
                if d_my <= d_op:
                    my_adv_sum += (1 if d_my == d_op else 2)  # closer or equal denies more
                if my_best is None or d_my < my_best:
                    my_best = d_my
                if opp_best is None or d_op < opp_best:
                    opp_best = d_op

            opp_min = opp_best if opp_best is not None else 0
            # Maximize capture, then denial advantage, then closeness to nearest resource, then keep near parity with opponent
            score = captured * 10**6 + my_adv_sum * 100 - my_min - (1 if opp_min < my_min else 0)
            key = (score, -my_adv_sum, -captured, -my_min, dx, dy)
        else:
            # No visible resources: move to center-ish while staying safe
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = cheb(nx, ny, int(cx), int(cy))
            score = -dist_center
            key = (score, dist_center, dx, dy)

        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best