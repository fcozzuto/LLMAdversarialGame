def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource deterministically: minimize (manhattan, y, x)
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def key_res(r):
        rx, ry = r
        return (man(rx, ry, sx, sy), ry, rx)

    target_x, target_y = min(resources, key=key_res)
    tx, ty = target_x, target_y

    # Opponent effect: slightly discourage moving closer to opponent unless it helps reach resources faster
    def dist_sq(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def obstacle_density(x, y):
        # count adjacent blocked cells (including diagonals) to avoid tight traps
        cnt = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                cnt += 1
        return cnt

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        base = -man(nx, ny, tx, ty)  # closer to target is better
        if (nx, ny) == (tx, ty):
            base += 1000  # grab
        # If there are other resources, slight bias to move toward the best among them
        # using a cheap second-choice estimate (avoid full search)
        second_best = None
        for r in resources:
            rx, ry = r
            if (rx, ry) == (tx, ty):
                continue
            d = man(nx, ny, rx, ry)
            if second_best is None or (d, ry, rx) < second_best:
                second_best = (d, ry, rx)
        if second_best is not None:
            base += -0.15 * second_best[0]

        # Avoid obstacles/traps
        base -= 0.5 * obstacle_density(nx, ny)

        # Mild contest pressure: prefer increasing distance from opponent
        base += 0.05 * dist_sq(nx, ny, ox, oy)

        # Tie-break deterministically by move preference order
        if base > best[1]:
            best = ((dx, dy), base)

    if best[0] is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0][0], best[0][1]]