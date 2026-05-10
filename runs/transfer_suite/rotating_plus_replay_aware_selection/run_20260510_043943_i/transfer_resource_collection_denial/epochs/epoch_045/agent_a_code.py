def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # pick best target by one-step race advantage (deterministic tie-break)
    best_r = resources[0]
    best_v = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        v = (do - ds) * 1000 - ds
        if ds == 0: v += 10**9
        if ds == 1: v += 5 * 10**5
        v += -(rx * 8 + ry) * 1e-6
        if v > best_v:
            best_v = v
            best_r = (rx, ry)
    tx, ty = best_r

    # choose move that maximizes next-turn race advantage toward chosen target
    best_m = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        score = (do2 - ds2) * 1000 - ds2
        # small preference to not step away from resources generally
        if ds2 == 0: score += 10**8
        if resources:
            score += -min(man(nx, ny, rx, ry) for rx, ry in resources) * 1e-3
        score += (dx * 0.0) + (dy * 0.0)
        if score > best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]