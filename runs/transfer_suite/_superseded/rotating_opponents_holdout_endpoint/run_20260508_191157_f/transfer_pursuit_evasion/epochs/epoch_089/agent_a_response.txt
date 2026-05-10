def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    oc = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    if role == "pursuer":
        tx = (ox + oc[0]) / 2.0
        ty = (oy + oc[1]) / 2.0
        best_score = None
        best_move = [0, 0]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    continue
                # Intercept by steering toward midpoint toward the evader's corner
                d_to_mid = abs(nx - tx) + abs(ny - ty)
                d_after = abs(nx - ox) + abs(ny - oy)
                score = (d_to_mid * 3.0) + (d_after * 1.0)
                if best_score is None or score < best_score:
                    best_score = score
                    best_move = [dx, dy]
        return best_move
    else:
        # Evader: move away from pursuer, toward the corner farthest from pursuer
        pc = min(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        far_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        tx, ty = (far_corner[0], far_corner[1]) if (abs(sx - far_corner[0]) + abs(sy - far_corner[1]) > 0) else pc
        best_score = None
        best_move = [0, 0]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    continue
                d_from_p = abs(nx - ox) + abs(ny - oy)
                d_to_corner = abs(nx - tx) + abs(ny - ty)
                # Prefer increasing separation primarily; corner-seeking secondarily
                score = (d_from_p * -1.0) + (d_to_corner * 0.3)
                if best_score is None or score < best_score:
                    best_score = score
                    best_move = [dx, dy]
        return best_move