def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    if not legal(sx, sy):
        for dx, dy in [(-1, -1),(0, -1),(1, -1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_targets = []
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            q = (0 if rx < W/2 else 1) + (0 if ry < H/2 else 2)  # deterministic tie-break
            best_targets.append((d_self, -(d_opp - d_self), q, rx, ry))
        best_targets.sort()
        tx, ty = best_targets[0][3], best_targets[0][4]
    else:
        tx, ty = W // 2, H // 2

    moves = [(-1, -1),(0, -1),(1, -1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cur_opp = cheb(sx, sy, ox, oy)
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target; slightly prefer not getting closer to opponent unless it also helps target.
        opp_pen = 0
        if d_o < cur_opp:
            opp_pen = (cur_opp - d_o) * 0.15
        # Mild preference to move in direction of target when tie.
        dir_pref = 0
        if cheb(nx, ny, tx, ty) == d_t:
            dir_pref = (abs(tx - nx) + abs(ty - ny)) * 0.001
        score = d_t + opp_pen + dir_pref
        if best is None or score < best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]