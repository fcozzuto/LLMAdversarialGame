def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade_mode = ("evad" in role) or ("run" in role) or ("away" in role) or ("escape" in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for ax, ay in deltas:
            nx, ny = x + ax, y + ay
            if ok(nx, ny):
                c += 1
        return c

    t = int(observation.get("turn_index", 0) or 0)
    shift = t % 9
    ordered = deltas[shift:] + deltas[:shift]

    best = (None, -10**9)
    cur_d = cheb(sx, sy, ox, oy)

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        nd = cheb(nx, ny, ox, oy)
        mob = mobility(nx, ny)

        # wall-robust tie-break: prefer moves that increase/decrease the larger component deterministically
        rx = (nx - ox)
        if rx < 0:
            rx = -rx
        ry = (ny - oy)
        if ry < 0:
            ry = -ry
        progress = (rx - ry)

        if evade_mode:
            # maximize distance; discourage stepping into "tighter" cells
            score = nd * 1000 + mob * 10 + progress
            if nd <= cur_d and (dx == 0 and dy == 0):
                score -= 50
        else:
            # minimize distance; if equal, favor higher mobility and progress that aligns with reducing separation component
            score = -nd * 1000 + mob * 10 + (-progress)
            if nd < cur_d:
                score += 200  # strong commitment when improving
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]