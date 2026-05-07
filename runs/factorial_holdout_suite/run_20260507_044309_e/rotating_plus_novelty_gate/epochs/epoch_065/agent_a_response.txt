def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def nearest_to(px, py):
        best = None; bestd = None
        for rx, ry in resources:
            d = cheb(px, py, rx, ry)
            if best is None or d < bestd or (d == bestd and (rx, ry) < best):
                best = (rx, ry); bestd = d
        return best, bestd

    opp_target, _ = nearest_to(ox, oy)
    my_target = None; best_gain = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds  # positive means we can arrive no later than opponent
        key = (gain, -do, -((rx + ry) & 7), rx, ry)
        if best_gain is None or key > best_gain:
            best_gain = key
            my_target = (rx, ry)

    tx, ty = my_target if my_target is not None else (w // 2, h // 2)

    # If opponent has a very close target and we are close enough to potentially steal, bias toward it.
    if opp_target is not None:
        rx, ry = opp_target
        if cheb(sx, sy, rx, ry) <= cheb(ox, oy, rx, ry):
            tx, ty = rx, ry

    best_move = (0, 0)
    best_key = None
    for dx, dy, nx, ny in valid:
        hit = (nx, ny) in set(map(tuple, resources))
        ds_after = cheb(nx, ny, tx, ty)
        do_to_target = cheb(ox, oy, tx, ty)
        # Prefer collecting now, otherwise minimize our distance while keeping competitive vs opponent
        key = (
            1 if hit else 0,
            (do_to_target - ds_after),  # bigger is better
            -ds_after,
            (nx + 2 * ny) % 11,
            dx, dy
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]