def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        bestd = -10**9
        for dx, dy, nx, ny in legal:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_r = None
    best_adv = -10**18
    best_sd = 10**18
    for r in resources:
        rx, ry = r
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best_r = r

    tx, ty = best_r
    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        val = d_t - 0.08 * d_o
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]