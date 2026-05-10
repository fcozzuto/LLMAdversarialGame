def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        feasible = 1 if my_d <= op_d else 0
        key = (feasible, op_d - my_d, -my_d, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    step_x = 0 if rx == sx else (1 if rx > sx else -1)
    step_y = 0 if ry == sy else (1 if ry > sy else -1)

    deltas = [(step_x, step_y), (step_x, 0), (0, step_y), (0, 0),
              (step_x, -step_y if step_y != 0 else 0), (-step_x if step_x != 0 else 0, step_y)]
    cur_best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = cheb(nx, ny, rx, ry)
            k = (-nd, 0 if (dx == 0 and dy == 0) else 1, -nx, -ny, dx, dy)
            if cur_best is None or k > cur_best:
                cur_best = k
                cur = (dx, dy)

    return [int(cur[0]), int(cur[1])] if cur_best is not None else [0, 0]