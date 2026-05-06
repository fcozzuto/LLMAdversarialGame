def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not free(sx, sy):
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            if free(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    def d(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    target = None
    best = None
    if resources:
        for r in resources:
            val = d((sx, sy), r)
            if best is None or val < best or (val == best and (r[0], r[1]) < target):
                best = val
                target = r

    cur_op_d = d((sx, sy), (ox, oy))
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if target is not None:
            score = -d((nx, ny), target)
            score2 = d((nx, ny), (ox, oy))
            score = (score, score2, -dx, -dy)
        else:
            score = (d((nx, ny), (ox, oy)), -nx, -ny, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]