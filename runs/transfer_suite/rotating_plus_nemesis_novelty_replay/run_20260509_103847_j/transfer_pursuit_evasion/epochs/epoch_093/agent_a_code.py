def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role) or ("runner" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        ax = abs(x - ox)
        ay = abs(y - oy)
        return ax if ax > ay else ay

    def free_neighbors(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if legal(nx, ny):
                c += 1
        return c

    def nearest_obstacle_dist(x, y):
        best = 999
        for (bx, by) in blocked:
            d = abs(bx - x) + abs(by - y)
            if d < best:
                best = d
        return best if blocked else 8

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny)
        mob = free_neighbors(nx, ny)
        obs_dist = nearest_obstacle_dist(nx, ny)
        if is_evader:
            # maximize distance, but also avoid getting trapped near obstacles
            val = (d * 1000) + (mob * 5) + (obs_dist)
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best_move)
        else:
            # minimize distance; additionally prefer moves that reduce opponent options (lower mobility)
            val = (-d * 1000) + (-mob * 5) + (obs_dist * 0.2)
            better = (best_val is None) or (val > best_val) or (val == best_val and (dx, dy) < best_move)
        if better:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]