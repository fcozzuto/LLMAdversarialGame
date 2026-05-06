def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = man(nx, ny, ox, oy)
            key = (d, man(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        my = man(x, y, rx, ry)
        opp = man(ox, oy, rx, ry)
        if my <= opp:
            key = (0, my, opp)
        else:
            key = (1, my - opp, my, opp)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = man(nx, ny, rx, ry)
        oppd = man(nx, ny, ox, oy)
        # If we are currently behind, prioritize gaining speed; otherwise prioritize being hard to contest.
        cur_my = best_key[1] if best_key[0] == 0 else best_key[1] + best_key[2]  # deterministic placeholder from key
        behind = 1 if (man(x, y, rx, ry) > man(ox, oy, rx, ry)) else 0
        key = (behind, myd, -oppd, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]