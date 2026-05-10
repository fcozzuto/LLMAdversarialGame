def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]
    tr = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = cheb(nx, ny, ox, oy) * 0.2 - cheb(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < bestm):
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # Evaluate positions by how much sooner we can reach a resource than opponent, plus a safety horizon.
    def pos_value(nx, ny):
        best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can arrive not later than opponent, strongly favor; otherwise still consider if opponent likely can't.
            arrive_adv = (do - ds)
            horizon = 1 if ds <= tr else -1
            # Tie-break: prefer closer resources once "advantage" is similar.
            v = arrive_adv * 1000 + horizon * 200 - ds * 3
            if v > best:
                best = v
        return best

    bestv = -10**18
    bestm = (0, 0)
    # Deterministic ordering by delta tuple to break ties consistently.
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        v = pos_value(nx, ny)
        # Mild preference for reducing distance to best current resource (stabilizes).
        best = resources[0]
        bs = cheb(sx, sy, best[0], best[1])
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bs:
                bs = d
                best = (rx, ry)
        v += -cheb(nx, ny, best[0], best[1]) * 0.01
        if v > bestv:
            bestv = v
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]