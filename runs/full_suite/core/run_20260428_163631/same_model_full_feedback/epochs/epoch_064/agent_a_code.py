def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dxdy = [0, 0]
    best_sc = -10**18

    # If no resources visible, drift to maximize distance from opponent corners bias.
    if not resources:
        tx = 0 if sx > (w - 1) / 2 else w - 1
        ty = 0 if sy > (h - 1) / 2 else h - 1
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sc = cheb(nx, ny, tx, ty) - 2 * cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_dxdy = [dx, dy]
        return best_dxdy

    # Target resource where opponent is relatively farther; also prefer being closer in absolute terms.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # immediate safety: avoid moving adjacent if possible
        opp_adj_pen = 0
        d_op = cheb(nx, ny, ox, oy)
        if d_op <= 1:
            opp_adj_pen = 4

        # compute best relative gain against any resource
        best_rel = -10**18
        best_abs = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            rel = op_d - my_d  # larger is better: opponent farther than me for that resource
            if rel > best_rel:
                best_rel = rel
            if my_d < best_abs:
                best_abs = my_d

        # Encourage closeness after securing relative advantage
        sc = 10 * best_rel - best_abs - opp_adj_pen

        # Minor tie-break: deterministic preference order via score then lexicographic
        if sc > best_sc:
            best_sc = sc
            best_dxdy = [dx, dy]

    return best_dxdy