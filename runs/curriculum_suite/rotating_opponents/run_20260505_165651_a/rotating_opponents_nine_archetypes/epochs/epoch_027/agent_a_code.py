def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose the resource that yields the highest "winning race" score for this move.
        cur_best = -10**18
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            adv = oppd - myd  # positive => we are closer
            # Strongly prefer taking resources we can reach first; otherwise, still pursue progress.
            s = 7 * adv - myd
            # If opponent is already extremely close, de-prioritize that resource.
            if oppd <= 1 and myd > oppd:
                s -= 50
            # Small tie-breaks to reduce oscillation and encourage moving toward cluster.
            s -= 0.01 * (rx + ry)
            if s > cur_best:
                cur_best = s

        # Secondary objective: avoid moves that increase our distance to all resources (stalling).
        my_closest = min(king_dist(nx, ny, rx, ry) for rx, ry in resources)
        score = (cur_best, -my_closest, nx, ny)
        if score > best:
            best = score

    return [best[2] - sx, best[3] - sy]