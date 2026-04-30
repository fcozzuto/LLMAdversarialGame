def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b, c, d):  # Chebyshev (diagonal friendly)
        dx = abs(a - c); dy = abs(b - d)
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            sd = dist(x, y, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner, and if close, prefer the ones further along for us
            score = (od - sd, -sd, rx, ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        target = best[1]
    else:
        target = (w - 1 - x, h - 1 - y)  # fallback drift

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        # Encourage reducing distance; slight preference for increasing opponent disadvantage
        val = (-d_self, d_opp - d_self, -(dx == 0 and dy == 0), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]