def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_val = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            if myd <= opd:
                # Prefer resources we can reach no later than opponent; maximize lead, also prefer shorter time.
                val = (opd - myd) * 4 - myd
            else:
                # If opponent gets it first, minimize the damage (prefer being as close as possible after they take/if contested).
                val = -(myd - opd) * 3 - myd
            if val > best_val:
                best_val = val
        if best_val > best[1]:
            best = ((dx, dy), best_val)
    return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]