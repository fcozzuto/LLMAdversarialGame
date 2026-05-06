def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid.append((x, y))

    if not valid:
        return [0, 0]

    # Intercept: go for resources where the opponent is already close.
    tx, ty = min(valid, key=lambda p: (man(p[0], p[1], ox, oy), man(p[0], p[1], sx, sy)))

    best = (10**18, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Encourage getting nearer to contested target; mildly discourage letting opponent be closer.
        penalty = 0
        if man(ox, oy, nx, ny) <= 1:
            penalty += 1
        val = self_d + 0.35 * opp_d + penalty
        if val < best[0]:
            best = (val, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [best[1][0], best[1][1]]