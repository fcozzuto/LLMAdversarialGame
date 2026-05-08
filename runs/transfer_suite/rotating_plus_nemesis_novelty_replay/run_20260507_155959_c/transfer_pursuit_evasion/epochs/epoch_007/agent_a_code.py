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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        wd = wall_dist(nx, ny)

        # Obstacle proximity (deterministic local "wall" signal)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    prox += 1

        # Pursuer: reduce distance, prefer closer-to-walls to constrain evader; also like proximity to obstacles
        # Evader: increase distance, prefer farther-from-walls, avoid obstacle proximity
        if pursuer:
            val = -d_opp + 0.15 * (-wd) + 0.06 * prox
        else:
            val = d_opp + 0.12 * wd - 0.08 * prox

        # Deterministic tie-break: smaller |dx| then smaller |dy| then lex
        tie = (abs(dx), abs(dy), dx, dy)
        cand = (val, tie)
        if best_val is None or cand > best_val:
            best_val = cand
            best = [dx, dy]
    return best