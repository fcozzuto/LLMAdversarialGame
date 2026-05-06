def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Innovate slightly: alternate target corner by parity to avoid symmetry stagnation
        tx, ty = (w - 1, h - 1) if (observation.get("turn_index", 0) % 2 == 0) else (0, h - 1)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_tar = abs(nx - tx) + abs(ny - ty)
            v = d_opp * 1000 - d_tar
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        nearest_self = 10**9
        nearest_opp = 10**9
        best_adv = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < nearest_self: nearest_self = sd
            if od < nearest_opp: nearest_opp = od
            adv = od - sd  # positive means we are closer than opponent
            if adv > best_adv: best_adv = adv
        # Prioritize winning a race (high advantage), then being closer; penalize giving opponent nearer access
        v = best_adv * 80 + (nearest_opp - nearest_self) * 10 - nearest_self
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]