def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            k = (cheb(nx, ny, tx, ty), dx, dy)
            if best is None or k < best:
                best = k
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    res_set = set(tuple(r) for r in resources)
    best_key = None
    best_move = (0, 0)

    for dx, dy, nx, ny in valid:
        collect_now = 1 if (nx, ny) in res_set else 0
        # Choose the resource that best swings advantage for us after this move
        best_adv = None
        best_d1 = None
        best_res = None
        for rx, ry in res_set:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            adv = d1 - d2
            if best_adv is None or (adv, d1, rx, ry) < (best_adv, best_d1, best_res[0], best_res[1]):
                best_adv, best_d1, best_res = adv, d1, (rx, ry)

        # Prefer immediate collection, then maximize advantage (min adv), then get close
        # Key sorts ascending: collect_now=1 should come first -> use -collect_now
        key = (-collect_now, best_adv, best_d1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]