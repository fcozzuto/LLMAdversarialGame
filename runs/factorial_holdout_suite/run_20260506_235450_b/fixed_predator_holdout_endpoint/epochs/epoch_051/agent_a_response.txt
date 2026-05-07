def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources_sorted = sorted((int(r[0]), int(r[1])) for r in resources)

    best = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if (dx != 0 or dy != 0) and not valid(nx, ny):
            continue

        # Choose the resource that maximizes our lead from the next position.
        local = -10**18
        my_opp_adj_pen = 0
        if (nx, ny) != (ox, oy):
            # Penalize moving into close contention distance with opponent.
            d = cheb(nx, ny, ox, oy)
            my_opp_adj_pen = d * 0.05

        for rx, ry in resources_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we can reach sooner (or contest less)
            # Prefer nearer resource if lead ties.
            val = lead * 10 - ds - my_opp_adj_pen
            if val > local:
                local = val

        if local > best:
            best = local
            best_move = [dx, dy]

    return best_move