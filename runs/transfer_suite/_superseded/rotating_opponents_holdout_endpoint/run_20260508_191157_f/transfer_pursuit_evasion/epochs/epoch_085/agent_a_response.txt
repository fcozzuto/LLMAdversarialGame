def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles", [])
    obs = {tuple(p) for p in obstacles}

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    dx_corner = 0 if target_corner[0] == ox else (1 if target_corner[0] > ox else -1)
    dy_corner = 0 if target_corner[1] == oy else (1 if target_corner[1] > oy else -1)

    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue

            if role == "pursuer":
                d1 = abs(nx - ox) + abs(ny - oy)
                ax = ox + dx_corner
                ay = oy + dy_corner
                if ax < 0 or ax >= w or ay < 0 or ay >= h or (ax, ay) in obs:
                    d2 = d1
                else:
                    d2 = abs(nx - ax) + abs(ny - ay)
                # If opponent is near a corner, prioritize capturing at the corner.
                corner_bias = 3 if (abs(ox - target_corner[0]) + abs(oy - target_corner[1])) <= 1 else 1
                val = corner_bias * d1 + 0.75 * d2
                better = val < best_val if best_val is not None else True
            else:
                d1 = abs(nx - ox) + abs(ny - oy)
                ax = ox + (-dx_corner)
                ay = oy + (-dy_corner)
                if ax < 0 or ax >= w or ay < 0 or ay >= h or (ax, ay) in obs:
                    d2 = d1
                else:
                    d2 = abs(nx - ax) + abs(ny - ay)
                # Prefer moving away from pursuit and toward safer space/corners.
                corner_bonus = 0.5 if (abs(target_corner[0] - nx) + abs(target_corner[1] - ny)) <= 1 else 0.0
                val = -(1.1 * d1 + 0.6 * d2) + corner_bonus
                better = val > best_val if best_val is not None else True

            if better or (best_val is not None and val == best_val and [dx, dy] < best_move):
                best_val = val
                best_move = [dx, dy]

    if best_move == [0, 0]:
        # Deterministic fallback: try smallest distance/ largest distance among legal moves including staying.
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs:
                    continue
                if role == "pursuer