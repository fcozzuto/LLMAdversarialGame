def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        wall_dist = min(nx, ny, (w - 1) - nx, (h - 1) - ny)  # bigger is safer for evader
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2)  # closer to center preferred by pursuer

        # Keep away from obstacles slightly by penalizing moves that land near them
        near_pen = 0
        for ax, ay in obs:
            if abs(ax - nx) + abs(ay - ny) == 1:
                near_pen -= 1
            elif abs(ax - nx) + abs(ay - ny) == 0:
                near_pen -= 5

        # Predict zigzag: prefer continuing the opponent's current direction relative to your move
        # Use opponent->you vector (simple proxy) to bias turning.
        # If you are pursuer: align to reduce both components; if evader: break alignment.
        comp_pen = -(abs(ddx) + abs(ddy))

        if is_evader:
            # Maximize distance, keep away from walls, and reduce capture alignment
            # Tie-break: prefer moves that increase comp_pen (less alignment) and slight center bias to avoid cornering too early.
            key = (d2, wall_dist, - (abs(ddx) + abs(ddy)), -center_bias, near_pen)
        else:
            # Minimize distance, avoid walls, and move toward center while aligning components
            key = (-d2, wall_dist * 0.5 + center_bias * 0.01, comp_pen, -abs(ddx) - abs(ddy), near_pen)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]