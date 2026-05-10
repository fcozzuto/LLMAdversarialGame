def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_value(x, y):
        if not inb(x, y) or (x, y) in obs:
            return -10**9
        if not resources:
            return 0
        best = -10**18
        for rx, ry in resources:
            myd = man(x, y, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Advantage race: lower my distance / higher opponent distance is better
            race = (opd - myd)
            # Slight preference to head toward resources that are close enough to matter
            urgency = 0.15 * (14 - myd)
            # Mild center bias for flexibility
            center = -0.01 * (abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0))
            best = max(best, race + urgency + center)
        return best

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    # Deterministic: prefer higher value, then lexicographically smaller delta
    best_delta = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        val = cell_value(nx, ny)
        key = (val, -dx, -dy)  # deterministic tie-break favoring smaller positive dx/dy less
        if val > best_val or (val == best_val and key > (best_val, -best_delta[0], -best_delta[1])):
            best_val = val
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]