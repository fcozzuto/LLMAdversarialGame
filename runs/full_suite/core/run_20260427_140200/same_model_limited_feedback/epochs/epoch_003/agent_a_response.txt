def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy) ** 0.5

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    # Contested targeting: prefer resources where we gain distance over opponent.
    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
                continue
            val = 0.0
            for rx, ry in resources:
                d_self = dist(nx, ny, rx, ry)
                d_opp = dist(ox, oy, rx, ry)
                # Favor resources we are closer to; if none, still move toward high-value ones.
                gain = d_opp - d_self
                val = max(val, gain * 10.0 - d_self)
            # Small bias to reduce distance to best currently targeted resource.
            # Evaluate against the best gain resource directly from next pos.
            if best is None:
                best = (dx, dy)
            if val > best_score:
                best_score = val
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # Fallback: obstacle-aware step toward center of remaining resources.
    if resources:
        tx = sum(r[0] for r in resources) / len(resources)
        ty = sum(r[1] for r in resources) / len(resources)
        # Prefer moving that most reduces distance to (tx, ty).
        bestd = 10**18
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
                continue
            d = dist(nx, ny, tx, ty)
            if d < bestd - 1e-9:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Last resort: avoid obstacles and move toward opponent to deny space.
    best = (0, 0)
    bestd = dist(sx, sy, ox, oy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles or (nx, ny) == (ox, oy):
            continue
        d = dist(nx, ny, ox, oy)
        if d < bestd:
            bestd = d
            best = (dx, dy)
    return [best[0], best[1]]