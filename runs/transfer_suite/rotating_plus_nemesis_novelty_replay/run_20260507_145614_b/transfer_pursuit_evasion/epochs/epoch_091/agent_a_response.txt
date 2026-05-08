def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    closest_corner = min(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))
    corner_dist2 = (ox - closest_corner[0]) * (ox - closest_corner[0]) + (oy - closest_corner[1]) * (oy - closest_corner[1])
    corner_near = 1.0 if corner_dist2 <= 2 else 0.0  # opponent really in/near a corner

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_d2(x, y):
        if not obst:
            return 10**9
        best = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_val = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, closest_corner[0], closest_corner[1])
        d_ob = nearest_obst_d2(nx, ny)
        obst_term = 0.25 / (1.0 + d_ob)  # prefer staying away from obstacles

        # If pursuer, reduce distance and additionally "pin" toward the corner when opponent is cornered.
        # If evader, increase distance and try to move toward the corner (consistent with evasion_corner).
        if is_pursuer:
            val = d_opp - (2.5 * corner_near) * d_corner + 1200.0 * obst_term
        else:
            val = -d_opp - (1.5 * corner_near) * d_corner + 1200.0 * obst_term

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]