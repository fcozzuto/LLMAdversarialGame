def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    def obs_near(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obs:
                c += 1
        return c

    cx, cy = w // 2, h // 2
    best = (0, 0); bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        base = -0.6 * cheb(nx, ny, cx, cy) - 0.4 * obs_near(nx, ny)

        if res:
            v = base
            for rx, ry in res:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach sooner; break ties by being closer.
                v += 2.2 * (od - md) - 0.18 * md
            # Slightly deter moving toward opponent
            v -= 0.06 * cheb(nx, ny, ox, oy)
        else:
            # No visible resources: move to improve position and keep distance from opponent
            v = 1.2 * cheb(nx, ny, ox, oy) + 0.2 * (-cheb(nx, ny, cx, cy)) - 0.4 * obs_near(nx, ny)

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]