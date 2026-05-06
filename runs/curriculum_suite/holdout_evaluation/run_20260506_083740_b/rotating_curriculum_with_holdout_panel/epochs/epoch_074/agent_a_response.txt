def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference order by closeness to center if tie
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if not resources:
        tx, ty = cx, cy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny) and nx - sx == dx and ny - sy == dy:
                return [dx, dy]
        # fallback
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    valid_resources = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose move that maximizes advantage for the best contestable resource,
        # then maximizes "speed" to it; finally prefers center progression.
        local_best_adv = -10**9
        local_best_spd = 10**9
        local_best_res = None
        for rx, ry in valid_resources:
            d_us = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            adv = d_op - d_us  # positive means we're closer than opponent
            spd = d_us
            key = (adv, -spd)
            # deterministic selection of resource per move
            if (local_best_res is None) or (adv > local_best_adv) or (adv == local_best_adv and spd < local_best_spd):
                local_best_adv, local_best_spd, local_best_res = adv, spd, (rx, ry)
        if local_best_res is None:
            continue
        center_prog = -(md(nx, ny, cx, cy))
        key = (local_best_adv, -local_best_spd, center_prog, nx, ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]