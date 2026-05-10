def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("evader" not in self_role) and ("purs" in self_role or self_role == "")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)
    def corners():
        return [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    opp_corners = corners()
    opp_corner = min(opp_corners, key=lambda c: manh(c[0], c[1], ox, oy))
    opp_corner_dist_from_opp = manh(opp_corner[0], opp_corner[1], ox, oy)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d = manh(nx, ny, ox, oy)
        if pursuer:
            # chase while edging opponent towards their nearest corner
            toward_corner = manh(nx, ny, opp_corner[0], opp_corner[1])
            # prefer reducing distance, and prefer being closer to opponent's nearest corner
            score = (-3 * d) + (-0.8 * toward_corner) + (0.4 * (opp_corner_dist_from_opp - manh(sx, sy, opp_corner[0], opp_corner[1])))
            # also prefer moving closer to boundary when it doesn't increase chase distance too much
            score += (0.3 * (edge_dist(sx, sy) - edge_dist(nx, ny)))
        else:
            # evade: maximize distance; also prefer farther from boundary only if it increases distance, otherwise corner farthest helps
            d_corner = min(manh(nx, ny, c[0], c[1]) for c in opp_corners)
            far_corner = max(opp_corners, key=lambda c: manh(c[0], c[1], ox, oy))
            toward_safe = -manh(nx, ny, far_corner[0], far_corner[1])
            score = (3 * d) + (0.3 * d_corner) + (0.8 * toward_safe) + (0.2 * edge_dist(nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]