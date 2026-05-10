def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_target():
        best = None
        best_score = -10**18
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if not inb(rx, ry):
                continue
            my_d = man(sx, sy, rx, ry)
            op_d = man(ox, oy, rx, ry)
            s = (op_d - my_d) * 100 - my_d * 2
            if my_d == 0:
                s += 500
            if op_d == 0:
                s -= 200
            if op_d < my_d:
                s -= 60
            if best is None or s > best_score:
                best_score = s
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = man(nx, ny, tx, ty)
        op_d = man(ox, oy, tx, ty)
        val = (op_d - my_d) * 100 - my_d * 2
        if my_d == 0:
            val += 500
        if dx == 0 and dy == 0:
            val -= 3
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return [best_move[0], best_move[1]]