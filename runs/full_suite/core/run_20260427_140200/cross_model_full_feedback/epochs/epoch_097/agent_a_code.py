def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        oppd = d(nx, ny, ox, oy)
        if resources:
            mind = 10**9
            for rx, ry in resources:
                if (rx, ry) not in obstacles:
                    dd = d(nx, ny, rx, ry)
                    if dd < mind:
                        mind = dd
            res_score = -mind
        else:
            res_score = -d(nx, ny, cx, cy)
        sc = 4 * oppd + 2 * res_score
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    if best_mv == (0, 0):
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
    return [best_mv[0], best_mv[1]]