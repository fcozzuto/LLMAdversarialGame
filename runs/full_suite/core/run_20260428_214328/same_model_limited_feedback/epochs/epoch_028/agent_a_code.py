def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources known: maximize distance from opponent while staying safe
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obs_set:
                    continue
                v = cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick a resource where we are relatively closer than opponent; otherwise closest to us.
    best_res = None
    best_b = None
    closest_m = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        b = opd - myd
        if closest_m is None or myd < closest_m[0]:
            closest_m = (myd, rx, ry)
        if best_b is None or b > best_b[0]:
            best_b = (b, rx, ry)
    if best_b[0] is not None and best_b[0] >= 0:
        tx, ty = best_b[1], best_b[2]
    else:
        tx, ty = closest_m[1], closest_m[2]

    # Choose move that improves distance to target and avoids opponent.
    best = [0, 0]
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_to_t = cheb(nx, ny, tx, ty)
            d_to_o = cheb(nx, ny, ox, oy)
            # Prefer getting closer to target; strongly prefer being farther from opponent.
            v = (-d_to_t * 5) + (d_to_o * 2)
            # Small tie-breaker: prefer moves that also reduce target distance from current.
            v += (cheb(sx, sy, tx, ty) - d_to_t) * 0.3
            if v > bestv:
                bestv = v
                best = [dx, dy]
    return best