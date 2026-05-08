def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr) or ("tagger" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def edge_prox(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def corner_target_score(x, y):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(dist2(x, y, cx, cy) for cx, cy in corners)

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        if pursuer:
            # minimize distance; also prefer moves that reduce escape space (closer to edge)
            score = -d - 0.08 * edge_prox(nx, ny)
        else:
            # maximize distance; prefer staying away from edge only if it doesn't reduce distance
            score = d + 0.02 * (7.0 - edge_prox(nx, ny)) + 0.01 * corner_target_score(nx, ny)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]