def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = observation.get("self_role", "")
    # Determine who is pursuer/evader by role names (robust to minor naming differences)
    self_is_pursuer = ("purs" in self_role.lower()) or ("catch" in self_role.lower())
    # If role is unclear, default to pursuer behavior (tends to score points)
    ox = opp_pos[0] - self_pos[0]
    oy = opp_pos[1] - self_pos[1]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        for ob in obstacles:
            if ob[0] == x and ob[1] == y:
                return True
        return False

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = self_pos[0] + dx, self_pos[1] + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        ddx = opp_pos[0] - nx
        ddy = opp_pos[1] - ny
        dist2 = ddx * ddx + ddy * ddy

        # Corner-cutting / interception style when pursuing:
        # also consider whether this move reduces distance while steering toward board center.
        if self_is_pursuer:
            center_x = (w - 1) / 2.0
            center_y = (h - 1) / 2.0
            center_dist = (center_x - nx) ** 2 + (center_y - ny) ** 2
            # Primary: minimize distance to opponent
            # Secondary: prefer smaller center distance to limit opponent escape space
            score = dist2 * 1000 + int(center_dist * 10)
            better = best_score is None or score < best_score or (score == best_score and (dx, dy) < best)
        else:
            # Evader: maximize distance, and prefer moving toward the opposite corner of the pursuer,
            # while discouraging getting stuck near obstacles (via checking next-step escape).
            dist_score = dist2
            far_cx = 0 if self_pos[0] <= (w - 1) / 2.0 else (w - 1)
            far_cy = 0 if self_pos[1] <= (h - 1) / 2.0 else (h - 1)
            corner_pref = (far_cx - nx) ** 2 + (far_cy - ny) ** 2

            # Escape check: count legal moves from the candidate square
            escape = 0
            for edx, edy in deltas:
                tx, ty = nx + edx, ny + edy
                if in_bounds(tx, ty) and not blocked(tx, ty):
                    escape += 1
            # Combine: maximize distance, then corner preference, then escape mobility
            score = dist_score * 1000 + int(corner_pref * 10) + escape
            better = best_score is None or score > best_score or (score == best_score and (dx, dy) < best)

        if better:
            best_score = score
            best = (dx, dy)

    # If all moves blocked/invalid, stay still
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]