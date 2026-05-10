def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def step_pen(nx, ny):
        pen = 0
        for dx in (-1, 0, 1):
            tx = nx + dx
            if tx < 0 or tx >= w:
                continue
            for dy in (-1, 0, 1):
                ty = ny + dy
                if dx == 0 and dy == 0:
                    continue
                if 0 <= ty < h and (tx, ty) in obs:
                    pen += 1
        return pen

    valid_resources = []
    for x, y in resources:
        x, y = int(x), int(y)
        if valid(x, y):
            valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    # Choose target resource where we have the biggest distance advantage.
    best_target = None
    best_key = None
    for rx, ry in valid_resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Key: maximize (opponent_distance - my_distance), then prefer smaller my distance, then deterministic tie-break.
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Pick move that reduces distance to target while avoiding obstacles.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd_after = cd(nx, ny, tx, ty)
        opd_now = cd(ox, oy, tx, ty)
        # Encourage gaining advantage on the target; slight penalty near obstacles.
        val = (opd_now - myd_after, -myd_after, -(step_pen(nx, ny)), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move