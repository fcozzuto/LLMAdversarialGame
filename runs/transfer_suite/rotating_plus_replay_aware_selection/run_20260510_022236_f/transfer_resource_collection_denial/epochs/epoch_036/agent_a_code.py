def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_list = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if inb(rx, ry) and (rx, ry) not in obs:
            res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    # Target resource: maximize how much closer we are than opponent.
    best = None
    best_key = (-10**18, -10**18)
    for rx, ry in res_list:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    def move_to(dx, dy):
        nx, ny = sx + dx, sy + dy
        return (dx, dy, nx, ny)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
    d = (desired_dx, desired_dy)
    nx, ny = sx + d[0], sy + d[1]
    if inb(nx, ny) and (nx, ny) not in obs:
        return [d[0], d[1]]

    # Fallback: pick best one-step option that avoids obstacles.
    best_m = (0, 0)
    best_s = (-10**18, 10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sdist = cheb(nx, ny, tx, ty)
        odist = cheb(ox, oy, tx, ty)
        k1 = odist - sdist
        k2 = sdist
        if (k1, -k2) > (best_s[0], -best_s[1]):
            best_s = (k1, k2)
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]