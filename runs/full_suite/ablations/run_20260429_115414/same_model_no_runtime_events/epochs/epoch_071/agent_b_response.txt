def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obstacle_pen(nx, ny):
        # discourage moving adjacent to obstacles (a stronger wall-avoidance than direct chasing)
        pen = 0
        for x, y in obstacles:
            if abs(x - nx) <= 1 and abs(y - ny) <= 1:
                if x != nx or y != ny:
                    pen += 2
        return pen

    # Evaluate each possible move by the best guaranteed target: maximize (opp_time - self_time)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose the most favorable resource for us from this next position
        best_res_val = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # margin: positive means we are closer (so we can secure it)
            margin = od - sd
            # secondary: prefer smaller our time, then away from opponent for later contest
            secondary = (sd * 2) + cheb(ox, oy, rx, ry) * 0.1
            v = (margin * 1000) - secondary - obstacle_pen(nx, ny)

            # deterministic tie-breaker: prefer higher v, then smaller (rx+ry), then lexicographic
            if best_res_val is None:
                best_res_val = (v, -(rx + ry), rx, ry)
            else:
                cand = (v, -(rx + ry), rx, ry)
                if cand > best_res_val:
                    best_res_val = cand

        if best_res_val is None:
            continue
        move_key = best_res_val[0], best_res_val[1], best_res_val[2], best_res_val[3], dx, dy
        if best_val is None or move_key > best_val:
            best_val = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]