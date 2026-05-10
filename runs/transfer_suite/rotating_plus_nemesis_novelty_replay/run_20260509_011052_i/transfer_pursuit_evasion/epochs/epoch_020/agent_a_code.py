def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    near_corner = min(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))
    far_corner = max(corners, key=lambda c: abs(ox - c[0]) + abs(oy - c[1]))

    step_to_near = (0 if ox == near_corner[0] else (1 if ox > near_corner[0] else -1),
                    0 if oy == near_corner[1] else (1 if oy > near_corner[1] else -1))
    trap_x, trap_y = ox - step_to_near[0], oy - step_to_near[1]  # between opponent and near corner
    if not (0 <= trap_x < w and 0 <= trap_y < h) or (trap_x, trap_y) in obstacles:
        trap_x, trap_y = ox, oy

    wall_dist = min(ox, w - 1 - ox, oy, h - 1 - oy)
    near_wall = 1 if wall_dist <= 2 else 0

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    best = (0, 0)
    best_score = -10**18

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_opp = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
            # If evader is cornering, cut off to the trap point; otherwise chase directly.
            tx, ty = (trap_x, trap_y) if near_wall else (ox, oy)
            d_target = abs(nx - tx) + abs(ny - ty)
            # Extra pressure: prefer moves that reduce distance to the near corner while also approaching.
            d_corner = abs(nx - near_corner[0]) + abs(ny - near_corner[1])
            # Small penalty for "wasting" by staying put when not adjacent.
            stay_pen = 0.6 if (dx == 0 and dy == 0 and d_opp >= 2) else 0.0
            score = (-2.4 * d_opp) + (-1.0 * d_target) + (-0.15 * d_corner) - stay_pen
            # If already very close, slightly prioritize immediate capture risk positioning (avoid cornering away).
            if d_opp <= 1:
                score += 0.35 * (-(abs(nx - far_corner[0]) + abs(ny - far_corner[1])))
            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]