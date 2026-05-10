def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_ev(r):
        r = (r or "").replace("-", "_")
        return ("evad" in r) or (r == "evader")

    def is_pu(r):
        r = (r or "").replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    if is_pu(self_role) and not is_ev(self_role):
        pursuer = True
    elif is_pu(opp_role) and not is_ev(opp_role):
        pursuer = False
    else:
        pursuer = True

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = -10**18 if pursuer else 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        dist = d2(nx, ny, ox, oy)

        # Boundary avoidance to reduce prior "hits boundary"
        boundary_pen = 0
        min_edge = min(nx, ny, (w - 1 - nx), (h - 1 - ny))
        boundary_pen = (4 - min_edge) if min_edge < 4 else 0

        # Corner-blocking bias: if opponent is near a corner, move to intercept along walls
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        nearest_corner_d = min(d2(nx, ny, cx, cy) for cx, cy in corners)
        opp_nearest_corner_d = min(d2(ox, oy, cx, cy) for cx, cy in corners)

        if pursuer:
            score = (-dist) - 2.0 * boundary_pen - 0.25 * nearest_corner_d
            # If opponent already near a corner, prioritize reducing distance to that corner
            score -= 0.2 * (nearest_corner_d if opp_nearest_corner_d <= 5 else 0)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            score = dist - 2.0 * boundary_pen + 0.15 * nearest_corner_d
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move