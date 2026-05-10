def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("evader" not in self_role) and ("purs" in self_role or self_role == "")

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    opp_corner = min(corners, key=lambda c: manh(ox, oy, c[0], c[1]))
    cx, cy = opp_corner

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        d_to_opp = manh(nx, ny, ox, oy)
        if pursuer:
            # chase, and additionally "trap" by nudging opponent toward their nearest corner
            d_opp_corner = manh(ox, oy, cx, cy)
            # estimate whether our move increases our ability to be closer to that corner line
            self_edge = edge_dist(nx, ny)
            # prefer reducing distance; slight preference for being close to opponent's corner (to block escapes)
            score = (-10.0 * d_to_opp) + (-0.15 * self_edge) + (0.02 * d_opp_corner)
        else:
            # evade: maximize distance while keeping some wall-avoidance to prevent corner-locks behind obstacles
            d = d_to_opp
            score = (10.0 * d) + (0.08 * edge_dist(nx, ny))

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]