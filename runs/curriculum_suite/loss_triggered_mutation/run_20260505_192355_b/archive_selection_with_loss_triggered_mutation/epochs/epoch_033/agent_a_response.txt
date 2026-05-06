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

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Choose the resource where we are (deterministically) the most ahead vs opponent.
        best_adv = None
        best_us = None
        best_res = None
        for rx, ry in resources:
            us = abs(nx - rx) + abs(ny - ry)
            op = abs(ox - rx) + abs(oy - ry)
            adv = op - us  # higher means we reach earlier
            key = (adv, -us, -abs(nx - rx), -abs(ny - ry), rx, ry)
            if best_adv is None or key > (best_adv, best_us, 0, 0, 0, 0):
                best_adv = adv
                best_us = us
                best_res = (rx, ry)
        rx, ry = best_res
        # Small tie-breakers to avoid oscillation: prefer moving to reduce distance to that target.
        my_dist = abs(nx - rx) + abs(ny - ry)
        op_dist = abs(ox - rx) + abs(oy - ry)
        key = (best_adv, -(my_dist - min(dist((sx, sy), (rx, ry)), 9999)), -(op_dist - dist((ox, oy), (rx, ry))), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]