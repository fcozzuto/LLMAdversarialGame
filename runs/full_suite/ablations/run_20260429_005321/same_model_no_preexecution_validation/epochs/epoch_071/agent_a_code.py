def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
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

    def best_for_move(nx, ny):
        if not free(nx, ny):
            return -10**18
        if (nx, ny) in res:
            return 10**6 - cheb(nx, ny, ox, oy)

        base = -0.25 * cheb(nx, ny, ox, oy) - 0.45 * obs_near(nx, ny)
        if not res:
            return base - 0.03 * cheb(nx, ny, w // 2, h // 2)

        # Score resources by how much sooner we can reach than opponent, with tie-break toward resource.
        best = -10**18
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Larger (od - sd) => we are ahead on that resource.
            rel = (od - sd)
            # Penalize being far from the resource to encourage progress.
            v = rel * 3.0 - sd * 0.35 - abs(sd - od) * 0.05
            if v > best:
                best = v
        return base + best

    best_move = (0, 0); best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = best_for_move(nx, ny)
        if v > best_val:
            best_val = v; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]