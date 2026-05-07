def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_penalty(start, target):
        # Penalize if an obstacle lies near the straight/diagonal approach direction.
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        stepx = 0 if dx == 0 else (1 if dx > 0 else -1)
        stepy = 0 if dy == 0 else (1 if dy > 0 else -1)
        x, y = start[0] + stepx, start[1] + stepy
        pen = 0
        for _ in range(3):  # local lookahead only
            if (x, y) in obstacles:
                pen += 2
            if (x, y) == target:
                break
            x += stepx
            y += stepy
            if not (0 <= x < w and 0 <= y < h):
                break
        return pen

    best_r = None
    best_key = None
    for r in resources:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        # Prefer winning races to resources: maximize (od - sd), then minimize sd, then farther from opponent.
        key = (-(od - sd), sd, -(abs(ox - r[0]) + abs(oy - r[1])), obstacle_penalty((sx, sy), r), r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]