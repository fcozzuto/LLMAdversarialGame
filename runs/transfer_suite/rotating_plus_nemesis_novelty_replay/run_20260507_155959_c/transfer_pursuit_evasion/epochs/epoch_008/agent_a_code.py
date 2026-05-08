def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr) or ("pursuer" in sr)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def obs_prox(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if pursuer:
        # Intercept by heading toward opponent's closest corner (cut off zigzags near edges)
        tx, ty = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    else:
        # Evade by heading toward the corner farthest from pursuer
        tx, ty = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_s = None
    best_m = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        wd = wall_dist(nx, ny)
        prox = obs_prox(nx, ny)
        # Simple deterministic corner-directing term
        corner_term = -(abs(nx - tx) + abs(ny - ty)) if pursuer else (abs(nx - tx) + abs(ny - ty))
        if pursuer:
            s = (-d) + 0.12 * wd + 0.35 * corner_term - 0.9 * prox
        else:
            s = (d) - 0.12 * wd + 0.35 * corner_term - 0.9 * prox
        if best_s is None or s > best_s:
            best_s = s
            best_m = [dx, dy]
    return [int(best_m[0]), int(best_m[1])]