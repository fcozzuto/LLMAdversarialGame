def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cand.append((dx, dy, nx, ny))

    if not resources:
        best = None
        for dx, dy, nx, ny in cand:
            v = -cheb((nx, ny), (ox, oy))
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    best_d = None
    for dx, dy, nx, ny in cand:
        best_here = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = cheb((nx, ny), (rx, ry))
            opp_d = cheb((ox, oy), (rx, ry))
            # Encourage taking resources that opponent is worse-positioned for; also avoid giving opponent advantage.
            v = (opp_d - our_d, -our_d)
            if best_here is None or v > best_here[0]:
                best_here = (v, rx, ry, our_d, opp_d)
        if best_here is None:
            continue
        (g, neg_our_d) = best_here[0]
        # If we are already adjacent to a resource, slightly prefer that move (more decisive).
        near_bonus = 1 if neg_our_d == 0 else 0
        total = (g, near_bonus, neg_our_d)
        if best_d is None or total > best_d[0]:
            best_d = (total, dx, dy)

    if best_d is None:
        # Fallback: move to reduce distance to opponent
        best = None
        for dx, dy, nx, ny in cand:
            v = -cheb((nx, ny), (ox, oy))
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]

    return [best_d[1], best_d[2]]