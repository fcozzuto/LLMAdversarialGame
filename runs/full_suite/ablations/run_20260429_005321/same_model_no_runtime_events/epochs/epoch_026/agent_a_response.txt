def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                dres = cheb(nx, ny, ox, oy)
                val = -dres
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
        return best_move

    # Choose action by "race" advantage: (opponent time - our time) to each resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        our_d_to_best = 10**9
        opp_d_to_best = 10**9
        best_race = -10**18
        # Evaluate best resource after taking this step.
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            nd = cheb(nx, ny, rx, ry)
            race = od - nd
            if race > best_race:
                best_race = race
                our_d_to_best = nd
                opp_d_to_best = od

        d_op = cheb(nx, ny, ox, oy)
        # Encourage reaching a resource sooner and maintain some distance from opponent.
        val = best_race * 10 - our_d_to_best - 0.2 * d_op + 0.05 * opp_d_to_best
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move