def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    role = (observation.get("self_role") or "").lower()
    is_pursuer = "pursuer" in role

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for ddx, ddy in deltas:
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    def nearest_obstacle_d2(x, y):
        best = 10**9
        for ax, ay in obstacles:
            ddx, ddy = x - ax, y - ay
            v = ddx * ddx + ddy * ddy
            if v < best:
                best = v
        return best if obstacles else best

    best_move = [0, 0]
    if is_pursuer:
        best_key = None  # minimize
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            d = dist2(nx, ny)
            mob = mobility(nx, ny)
            obs_d = nearest_obstacle_d2(nx, ny)
            ax = 1 if ox > nx else (-1 if ox < nx else 0)
            ay = 1 if oy > ny else (-1 if oy < ny else 0)
            align = -((ddx - ax) * (ddx - ax) + (ddy - ay) * (ddy - ay))
            key = (d, -mob, -obs_d, align, ddx, ddy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [ddx, ddy]
    else:
        best_key = None  # minimize with negated distance
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not in_bounds(nx, ny) or (nx, ny) in obs:
                continue
            d = dist2(nx, ny)
            mob = mobility(nx, ny)
            obs_d = nearest_obstacle_d2(nx, ny)
            ax = 1 if ox > nx else (-1 if ox < nx else 0)
            ay = 1 if oy > ny else (-1 if oy < ny else 0)
            flee_align = -((ddx + ax) * (ddx + ax) + (ddy + ay) * (ddy + ay))
            # Prefer larger distance, then larger mobility, then staying away from obstacles, then break ties deterministically
            key = (-d, -mob, -obs_d, -flee_align, ddx, ddy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [ddx, ddy]

    return [int(best_move[0]), int(best_move[1])]