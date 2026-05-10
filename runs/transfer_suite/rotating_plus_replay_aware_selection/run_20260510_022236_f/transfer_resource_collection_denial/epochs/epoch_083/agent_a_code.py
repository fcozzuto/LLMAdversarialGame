def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for x, y in resources:
        x, y = int(x), int(y)
        if inb(x, y) and (x, y) not in obs:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Primary: maximize advantage (opponent arrival later). Secondary: minimize own distance.
            adv = do - ds
            valid.append((adv, -ds, x, y))
    if not valid:
        return [0, 0]

    valid.sort(reverse=True)
    tx, ty = valid[0][2], valid[0][3]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic evaluation order: prefer steps that get us closer to target; break ties by staying closer to safety from opponent.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = cheb(nx, ny, tx, ty)
        d2 = cheb(nx, ny, ox, oy)
        scored.append((-d1, d2, dx, dy))
    if not scored:
        return [0, 0]

    scored.sort(reverse=True)
    return [int(scored[0][2]), int(scored[0][3])]