def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obst = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    legal = []
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Escape if very close to opponent: maximize distance from them, but don't walk into walls/obstacles.
    if d2(x, y, ox, oy) <= 2:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = d2(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best[0]):
                bestv = v
                best = (dx, dy, nx, ny)
        return [best[0], best[1]]

    # Choose a target resource: maximize "reach advantage" (opponent far, we near).
    # If no resource gives reach advantage, choose the closest one to us.
    if resources:
        best_target = None
        best_adv = -10**18
        fallback_target = None
        fallback_d = 10**18
        for rx, ry in resources:
            md = d2(x, y, rx, ry)
            od = d2(ox, oy, rx, ry)
            if md < fallback_d or (md == fallback_d and (rx, ry) < tuple(fallback_target) if fallback_target else True):
                fallback_d = md
                fallback_target = (rx, ry)
            adv = od - md
            if od > md:  # only consider genuine advantage
                if adv > best_adv or (adv == best_adv and (rx, ry) < best_target):
                    best_adv = adv
                    best_target = (rx, ry)
        target = best_target if best_target is not None else fallback_target
    else:
        # No resources visible: drift toward center (avoid opponent a bit).
        target = (w // 2, h // 2)

    tx, ty = target

    # Move: decrease distance to target, but penalize moving closer to opponent to reduce interference.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = -d2(nx, ny, tx, ty)
        # Reduce chance of getting "stolen" by the opponent by keeping separation.
        v -= 0.15 * d2(nx, ny, ox, oy)
        # Prefer lateral progress over staying still when not beneficial.
        if dx == 0 and dy == 0:
            v -= 0.02
        if v > bestv or (v == bestv and (dx, dy) < best[:2] if best else True):
            bestv = v
            best = (dx, dy, nx, ny)

    return [best[0], best[1]]