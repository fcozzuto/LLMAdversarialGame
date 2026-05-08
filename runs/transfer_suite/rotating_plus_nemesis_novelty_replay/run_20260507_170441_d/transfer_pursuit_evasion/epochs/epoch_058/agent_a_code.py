def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    target_dx = 0 if ox == sx else (1 if ox > sx else -1)
    target_dy = 0 if oy == sy else (1 if oy > sy else -1)

    pref = [
        [target_dx, target_dy], [target_dx, 0], [0, target_dy],
        [target_dx, -target_dy], [-target_dx, target_dy],
        [0, 0],
        [-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]
    ]
    seen = set()
    dirs = []
    for d in pref:
        dx, dy = int(d[0]), int(d[1])
        if dx < -1 or dx > 1 or dy < -1 or dy > 1:
            continue
        key = (dx, dy)
        if key not in seen:
            seen.add(key)
            dirs.append(key)

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        align = 0
        if nx == ox:
            align = 1
        if ny == oy:
            align = 1
        score = (dist, -align, dx == 0 and dy == 0, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]