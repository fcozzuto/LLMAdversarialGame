def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_prox(x, y):
        pen = 0
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        return pen

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w - 1 - ox, h - 1 - oy
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), obstacle_prox(nx, ny), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best:
            return [best[1], best[2]]
        return [0, 0]

    best_res = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we're closer to than opponent (large od - sd), then closer itself
        key = (-(od - sd), sd, abs(rx - (w // 2)) + abs(ry - (h // 2)), rx, ry)
        if best_res is None or key < best_res[0]:
            best_res = (key, rx, ry)
    tr, ty = best_res[1], best_res[2]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_new = man(nx, ny, tr, ty)
        od = man(ox, oy, tr, ty)
        # Maximize our advantage; also minimize obstacle proximity and distance to target
        adv = od - sd_new
        key = (-adv, sd_new, obstacle_prox(nx, ny), abs(nx - tr) + abs(ny - ty), dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)
    if best_move:
        return [best_move[1], best_move[2]]
    return [0, 0]