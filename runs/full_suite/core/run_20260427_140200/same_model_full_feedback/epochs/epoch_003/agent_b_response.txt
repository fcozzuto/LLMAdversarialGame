def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    # If no resources, head to a corner away from opponent.
    if not resources:
        tx = 0 if ox > (w - 1) // 2 else (w - 1)
        ty = 0 if oy > (h - 1) // 2 else (h - 1)
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best_move = (0, 0)
    best_val = -10**18

    # Score move by best "winning" resource: larger (opp_dist - self_dist) is better.
    # Add small tie-breakers to prefer closer resources and safer squares.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Safety: count free neighboring squares (deterministic local heuristic).
        free_n = 0
        for adx, ady in dirs:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) not in obs:
                free_n += 1

        best_resource_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Want to be earlier: maximize do - ds. Penalize if too far.
            v = (do - ds) * 100 - ds
            # Slightly prefer central-ish when contested value equal.
            v += -abs(rx - (w - 1) / 2) * 0.01 - abs(ry - (h - 1) / 2) * 0.01
            if v > best_resource_val:
                best_resource_val = v

        total = best_resource_val + free_n * 0.5
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]