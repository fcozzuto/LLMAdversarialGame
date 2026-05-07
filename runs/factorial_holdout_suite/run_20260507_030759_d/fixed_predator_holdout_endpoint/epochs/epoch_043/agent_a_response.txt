def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set(map(tuple, obstacles))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    if (sx, sy) in obs:
        return [0, 0]
    if (sx, sy) in set(map(tuple, resources)):
        return [0, 0]

    ox, oy = observation["opponent_position"]

    def cell_pen(x, y):
        if (x, y) in obs:
            return 10**9
        p = 0
        for ax, ay in obstacles:
            dx = x - ax
            dy = y - ay
            d = abs(dx) if abs(dx) > abs(dy) else abs(dy)
            if d == 0:
                return 10**9
            if d == 1:
                p += 20
            elif d == 2:
                p += 6
        return p

    if not resources:
        tx, ty = w // 2, h // 2
        return [sign(tx - sx), sign(ty - sy)]

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are already closer; otherwise race the most contested.
        adv = od - sd
        # Slightly prefer central and safer paths.
        center = abs(rx - (w // 2)) + abs(ry - (h // 2))
        safe_bias = -(min(abs(rx - ax) + abs(ry - ay) for ax, ay in obstacles) if obstacles else 99)
        key = (adv, -sd, -safe_bias, -center)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Choose the best immediate step by 1-step value: reduce distance to target, keep safe, avoid opponent.
    best_step = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        ns = abs(tx - nx) + abs(ty - ny)
        no = abs(tx - ox) + abs(ty - oy)  # stable baseline for target
        opp_focus = abs(nx - ox) + abs(ny - oy)
        val = (-ns) + (opp_focus == 0) * -1000  # discourage moving into opponent
        val -= cell_pen(nx, ny) * 0.1
        # If we can grab a resource now, prioritize strongly.
        if (nx, ny) in set(map(tuple, resources)):
            val += 10000
        if val > best_val:
            best_val = val
            best_step = (dx, dy)
    return [best_step[0], best_step[1]]