def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_here = (nx, ny)
        # Prefer resources where we can get an approach-time lead; use Chebyshev for diagonal speed.
        local_best = -10**18
        for rx, ry in resources:
            rcell = (rx, ry)
            sd = cheb(my_here, rcell)
            od = cheb((ox, oy), rcell)
            lead = od - sd
            # Encourage actually being closer and being "ahead" even if tied.
            val = lead * 10 - sd
            if val > local_best:
                local_best = val

        # Break ties deterministically: prefer moves that keep us progressing toward the best resource
        # and avoid drifting away from the opponent too slowly.
        if local_best > best_val:
            best_val = local_best
            best = (dx, dy)
        elif local_best == best_val:
            # secondary: minimize our distance to the currently most urgent resource by our advantage metric
            tie_best = None
            for rx, ry in resources:
                sd = cheb((nx, ny), (rx, ry))
                od = cheb((ox, oy), (rx, ry))
                if tie_best is None or (od - sd) > tie_best[0] or ((od - sd) == tie_best[0] and sd < tie_best[1]):
                    tie_best = (od - sd, sd)
            best_comp = best
            bx, by = sx + best_comp[0], sy + best_comp[1]
            cur_best = None
            for rx, ry in resources:
                sd = cheb((bx, by), (rx, ry))
                od = cheb((ox, oy), (rx, ry))
                if cur_best is None or (od - sd) > cur_best[0] or ((od - sd) == cur_best[0] and sd < cur_best[1]):
                    cur_best = (od - sd, sd)
            if tie_best is not None and (cur_best is None or tie_best[1] < cur_best[1]):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]