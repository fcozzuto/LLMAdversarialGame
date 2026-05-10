def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role) and not is_evader(opp_role):
        pursuer = False
    elif not pursuer and is_pursuer(opp_role) and is_evader(opp_role):
        pursuer = True
    elif pursuer and is_evader(self_role):
        pursuer = False

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_score = None
    # deterministic move order: bias towards cardinal/diagonal spread
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        d_to_opp = dist2(nx, ny, ox, oy)
        # obstacle "shelter": count blocked adjacent moves
        blocked = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (not in_bounds(xx, yy)) or ((xx, yy) in obs):
                    blocked += 1
        # pursuer wants closer to opponent; evader wants farther and near shelter/corner
        if pursuer:
            corner_pull = dist2(nx, ny, far_corner[0], far_corner[1])
            score = (-d_to_opp) - 0.01 * corner_pull + 0.02 * blocked
        else:
            corner_favor = dist2(nx, ny, far_corner[0], far_corner[1])
            score = (d_to_opp) + 0.02 * blocked + 0.01 * corner_favor

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]