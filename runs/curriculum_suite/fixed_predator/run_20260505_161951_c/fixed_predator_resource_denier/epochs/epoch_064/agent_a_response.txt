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
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0)
        bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
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

        # Evaluate move by its best "beat or deny" outcome.
        movev = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer cells where we arrive strictly earlier (take), else where we can contest/deny.
            if d_me < d_op:
                v = 2000 + (d_op - d_me) * 50 - (abs(rx - (nx)) + abs(ry - (ny))) * 0.1
            else:
                v = 500 - (d_me - d_op) * 60 - (abs(rx - (nx)) + abs(ry - (ny))) * 0.1
            # Extra bias toward approaching a single global target to avoid indecision.
            v += -cheb(nx, ny, w - 1, h - 1) * 0.5
            if v > movev:
                movev = v
        # Also add immediate "opponent pressure": move to increase our advantage over their position.
        movev += (cheb(nx, ny, ox, oy) * 2)

        if movev > bestv or (movev == bestv and (dx, dy) < best):
            bestv = movev
            best = (dx, dy)

    return [best[0], best[1]]