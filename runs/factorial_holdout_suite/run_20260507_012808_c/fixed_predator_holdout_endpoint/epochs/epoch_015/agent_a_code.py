def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_move_toward(target_x, target_y):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sc = (-md(nx, ny, target_x, target_y), md(nx, ny, ox, oy))
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    if res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sd = 10**18
            od = 10**18
            for rx, ry in res:
                d1 = md(nx, ny, rx, ry)
                if d1 < sd:
                    sd = d1
                d2 = md(ox, oy, rx, ry)
                if d2 < od:
                    od = d2
            sc = (od - sd, -sd, od)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    cx, cy = w // 2, h // 2
    return best_move_toward(cx, cy)