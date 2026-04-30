def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def cheb_dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Select a target resource that is better than what the opponent can reach
    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            myd = cheb_dist(x, y, rx, ry)
            opd = cheb_dist(ox, oy, rx, ry)
            val = myd - opd  # smaller is better (prefer resources we're at least as close to)
            if best is None or val < best[0] or (val == best[0] and (rx, ry) < best[1]):
                best = (val, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources known: drift toward opponent-less center-ish by targeting opponent direction
        tx, ty = w // 2, h // 2

    moves = [-1, 0, 1]
    options = []
    for dx in moves:
        for dy in moves:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist_t = cheb_dist(nx, ny, tx, ty)
            dist_o = cheb_dist(nx, ny, ox, oy)
            # Prefer reducing distance to target; mildly prefer staying away from opponent
            score = -(dist_t * 10) + (dist_o)
            # Deterministic tie-break: lexicographic preference on (dx,dy)
            options.append((score, dx, dy))
    if not options:
        return [0, 0]
    options.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [options[0][1], options[0][2]]