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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    t = int(observation.get("turn_index") or 0)

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my_best = -10**18
            # Choose a target that we are relatively closer to than the opponent
            for tx, ty in resources:
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                # Favor: we are much closer; also avoid too far overall
                score = (opd - myd) * 10 - myd
                # Small deterministic preference to break ties
                score += ((nx + ny + tx + ty + t) & 1) * 0.01
                if score > my_best:
                    my_best = score
            if my_best > best_score:
                best_score = my_best
                best_move = [dx, dy]
    else:
        # No resources visible: advance toward opponent's side while avoiding getting too close
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer moves that reduce distance to center and increase distance from opponent
            d_center = cheb(nx, ny, cx, cy)
            d_opp = cheb(nx, ny, ox, oy)
            score = -d_center + d_opp * 0.5 + ((nx + ny + t) & 1) * 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move