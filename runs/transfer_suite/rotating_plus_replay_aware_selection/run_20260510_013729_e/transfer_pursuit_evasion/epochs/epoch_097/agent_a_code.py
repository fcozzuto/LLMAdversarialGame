def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    act_as_evader = self_ev or (not opp_ev and self_role == "" and not ("purs" in self_role or "hunt" in self_role))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # chebyshev

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = dist((sx, sy), (ox, oy))

    # Evader prefers to go toward the farthest corner from pursuer; pursuer heads directly toward evader.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        d = dist((nx, ny), (ox, oy))
        if act_as_evader:
            # maximize separation; add mild preference for staying away from the nearest corner linearly
            score = d * 1000 + (abs(nx - far_corner[0]) + abs(ny - far_corner[1]))
            # also discourage moving closer than current if possible
            if d < cur_d:
                score -= 50
        else:
            # minimize separation; if equal, prefer alignment toward opponent
            score = -d * 1000 - (abs(nx - ox) + abs(ny - oy))
            # discourage stepping into squares that keep us from approaching (tie-breaker)
            if d > cur_d:
                score -= 50

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]