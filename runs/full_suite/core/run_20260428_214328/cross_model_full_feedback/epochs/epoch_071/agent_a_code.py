def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my_pos = (sx, sy)
    op_pos = (ox, oy)

    # Intercept opponent's nearest resource if we can match or beat the contest distance.
    best_op = None
    best_opd = None
    for r in resources:
        d = cheb(op_pos, r)
        if best_opd is None or d < best_opd:
            best_opd = d
            best_op = r

    myd_to_op = cheb(my_pos, best_op) if best_op is not None else 10**9

    if best_op is not None and myd_to_op <= best_opd:
        target = best_op
        intercept = True
    else:
        target = min(resources, key=lambda r: cheb(my_pos, r))
        intercept = False

    tx, ty = int(target[0]), int(target[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            val = -10**18
        else:
            nd_my = cheb((nx, ny), (tx, ty))
            nd_op = cheb(op_pos, (tx, ty))
            if intercept:
                val = (1000 - nd_my) + (nd_op - best_opd) * 50
            else:
                # Go for our closest while also pulling opponent away from our target.
                val = (200 - nd_my) + (nd_op) * 5
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]