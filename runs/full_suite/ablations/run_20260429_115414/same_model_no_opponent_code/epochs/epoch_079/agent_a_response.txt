def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Fall back: stay away from opponent while remaining valid
        best_s = -10**9
        best_m = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            s = cheb(nx, ny, ox, oy)
            if s > best_s:
                best_s, best_m = s, (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    # Evaluate moves by racing: choose the best target for the resulting position, then maximize advantage.
    best_total = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        move_best = -10**18
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Advantage: prefer targets where we are closer; break ties by shorter absolute distance.
            margin = do - ds
            s = margin * 100 - ds
            if s > move_best:
                move_best = s

        # Secondary: avoid moving into cells that worsen our best target too much (stability)
        # and slightly avoid getting too close to opponent unless it helps winning targets.
        opp_close_pen = cheb(nx, ny, ox, oy)
        total = move_best * 3 + opp_close_pen
        if total > best_total:
            best_total, best_move = total, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]