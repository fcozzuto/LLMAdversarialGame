def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or (("purs" not in self_role and "chase" not in self_role) and (("evad" in opp_role) or ("escape" in opp_role) or ("runner" in opp_role)))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_score(x, y):
        best = 10**9
        for cx, cy in corners:
            d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if d < best:
                best = d
        return best

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    # If we are pursuer: minimize distance; encourage pushing toward nearest corner of opponent.
    # If we are evader: maximize distance; head toward farthest corner.
    # Add small obstacle penalty via forced "stay near open space" heuristic.
    def open_neighbors(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                cnt += 1
        return cnt

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        oc = open_neighbors(nx, ny)
        ncc = nearest_corner_score(nx, ny)
        if i_am_evader:
            # Prefer far from pursuer and toward farthest corner (maximize corner distance from nearest corner -> which is monotonic inverse, so use -ncc)
            score = (10_000 * d) + (2_000 * oc) - (1 * ncc)
        else:
            # Prefer close to pursuer; also try to move in direction that makes opponent closer to a corner by approximating: minimize our corner distance after move? (keeps us aligned)
            score = (-10_000 * d) + (2_000 * oc) - (1 * ncc)
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]