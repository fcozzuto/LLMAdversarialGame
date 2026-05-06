def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy, nx, ny in legal:
            key = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # higher means we are closer
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    cur_adv = man(ox, oy, rx, ry) - man(sx, sy, rx, ry)

    # Prefer moves that (1) reduce distance to target, (2) improve advantage vs opponent, (3) avoid getting stuck
    best = None
    for dx, dy, nx, ny in legal:
        nd = man(nx, ny, rx, ry)
        nadv = man(ox, oy, rx, ry) - nd
        opp_to_target = man(nx, ny, ox, oy)
        key = (-(nadv - cur_adv), nd, opp_to_target, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]