def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    if not resources:
        return [0, 0]

    # Pick best few targets by "reach race" advantage.
    scored_targets = []
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        key = (opd - myd, -myd, -rx, -ry)
        scored_targets.append((key, rx, ry))
    scored_targets.sort(key=lambda t: t[0], reverse=True)
    targets = [(t[1], t[2]) for t in scored_targets[:3]]  # top-3 deterministically

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None  # (score, dx, dy)
    for rx, ry in targets:
        for dx, dy, nx, ny in moves:
            myd2 = kdist(nx, ny, rx, ry)
            opd2 = kdist(ox, oy, rx, ry)  # opponent stays for 1-step eval
            # Prefer winning race, then shorter self distance, then more "toward target"
            score = (opd2 - myd2, -myd2, -(abs(nx - sx) + abs(ny - sy)), -rx, -ry)
            if best is None or score > best[0]:
                best = (score, dx, dy)

    return [best[1], best[2]]