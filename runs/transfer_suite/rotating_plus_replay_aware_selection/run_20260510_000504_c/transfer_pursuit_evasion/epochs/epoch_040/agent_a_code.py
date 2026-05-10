def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    i_am_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("hunter" in self_role)
    if not i_am_pursuer:
        if ("purs" in opp_role) or ("chase" in opp_role) or ("hunter" in opp_role):
            i_am_pursuer = False
        else:
            i_am_pursuer = ("evad" not in self_role) and ("escap" not in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    if i_am_pursuer:
        target_corner = min(corners, key=lambda p: dist2(p[0], p[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = dist2(nx, ny, ox, oy)
            d_opp_to_corner = dist2(ox, oy, target_corner[0], target_corner[1])
            # Prefer immediate capture, then minimize distance; tie-break by pushing opp toward corner and reduce our drift.
            score = 10**9 - d_to_opp
            if d_to_opp == 0:
                score += 10**10
            score += -2 * d_opp_to_corner
            # slight preference for forward progress toward corner as pursuer
            score += -dist2(nx, ny, target_corner[0], target_corner[1]) // 3
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        return list(best) if best is not None else [0, 0]
    else:
        # Evader: move to maximize distance from pursuer; prefer farthest corner, avoid obstacles.
        target_corner = max(corners, key=lambda p: dist2(p[0], p[1], ox, oy))
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_from_p = dist2(nx, ny, ox, oy)
            d_to_corner = dist2(nx, ny, target_corner[0], target_corner[1])
            # Prefer staying not captured (maximize distance), then move toward chosen corner, discourage "near-corner dead ends".
            score = d_from_p * 10 - d_to_corner
            if d_from_p == 0:
                score -= 10**12
            if best is None or score > best_score:
                best = (dx, dy)
                best_score = score
        return list(best) if best is not None else [0, 0]