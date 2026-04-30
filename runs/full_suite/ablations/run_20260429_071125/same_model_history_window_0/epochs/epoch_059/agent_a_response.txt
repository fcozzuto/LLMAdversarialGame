def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev
    # pick target resource that I can secure (minimize my_dist - opp_dist), tie-break by my_dist
    if resources:
        best = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            adv = myd - opd
            key = (adv, myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        target = best[1]
    else:
        target = (w // 2, h // 2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # prefer moves that go to target while avoiding obstacles; if blocked, pivot to a safe/advantageous alternative
    def eval_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return None
        d_to_t = dist((nx, ny), target)
        d_to_o = dist((nx, ny), (ox, oy))
        # discourage stepping closer when contested
        contested = 1 if resources and any(dist((ox, oy), tuple(r)) < dist((sx, sy), tuple(r)) for r in resources) else 0
        return (d_to_t, -d_to_o if contested else d_to_o, dx, dy)

    bestm = None
    for dx, dy in deltas:
        ev = eval_move(dx, dy)
        if ev is None:
            continue
        if bestm is None or ev < bestm[0]:
            bestm = (ev, [dx, dy])

    if bestm is not None:
        return bestm[1]

    # fallback: stay (valid and deterministic)
    return [0, 0]