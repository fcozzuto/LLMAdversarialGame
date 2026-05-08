def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evader" in role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_list = list(obstacles)

    def nearest_obstacle_dist(x, y):
        md = 99
        for ax, ay in obs_list:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if obs_list else 99

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    # Prefer moves that approach (pursuer) or flee (evader) while also steering away from nearby obstacles.
    best_dxdy = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        dob = nearest_obstacle_dist(nx, ny)

        # Obstacle repulsion when close; slight tie-break toward center to avoid corner traps.
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.02
        obstacle_term = (dob if dob < 99 else 10)  # capped implicitly by scale below
        if dob <= 1:
            obstacle_pen = -100.0
        else:
            obstacle_pen = (dob - 2) * 1.5  # reward staying a bit away

        # Simple "intercept": for pursuer, also prefer reducing distance in both axes; for evader, prefer increasing it.
        axis_term = - (abs(nx - ox) + abs(ny - oy)) * (0.01 if is_evader else -0.01)
        # More direct goal term:
        goal_term = dist if is_evader else -dist

        score = goal_term + obstacle_pen + center_bias + axis_term

        if best_score is None or score > best_score:
            best_score = score
            best_dxdy = [dx, dy]
        elif score == best_score:
            # Deterministic lexicographic tie-break favoring smaller dx then dy, then staying still.
            if (dx, dy) < (best_dxdy[0], best_dxdy[1]):
                best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]