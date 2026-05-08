def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    self_is_pursuer = ("purs" in srole) and ("evad" not in srole)
    if ("purs" not in srole) and ("purs" in orole):
        self_is_pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def score_cell(nx, ny):
        d = dist(nx, ny, ox, oy)  # manhattan; capture radius is 0
        # Reward/penalize moving around obstacles by preferring cells with more free neighbors.
        free_n = 0
        for mx, my in moves:
            tx, ty = nx + mx, ny + my
            if legal(tx, ty):
                free_n += 1
        if self_is_pursuer:
            # Chase: minimize distance; tie-break by maximizing free space and avoiding "center stalls"
            return (-d, free_n, -(abs(nx - ox) + abs(ny - oy)))
        else:
            # Evader: maximize distance; tie-break by maximizing free space
            return (d, free_n, -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)))

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        k = score_cell(nx, ny)
        if best is None or k > best_key:
            best = (dx, dy)
            best_key = k

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]