def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obstacles(nx, ny):
        c = 0
        if (nx - 1, ny) in obs: c += 1
        if (nx + 1, ny) in obs: c += 1
        if (nx, ny - 1) in obs: c += 1
        if (nx, ny + 1) in obs: c += 1
        return c

    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty)) - adj_obstacles(nx, ny) * 3
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        ao = adj_obstacles(nx, ny)
        # Maximize "resource taking advantage": opp_cheb - self_cheb, with a self-time penalty.
        best_res = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self  # positive means we can reach before/at same speed
            v = adv * 120 - d_self * 3 - ao * 4
            if v > best_res:
                best_res = v
        # Prefer cells that improve some resource interaction and don't overstay.
        if best_res > bestv or (best_res == bestv and (dx, dy) < best):
            bestv = best_res
            best = (dx, dy)
    return [best[0], best[1]]