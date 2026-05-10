def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = observation.get("self_role") or "pursuer"

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if (sx, sy) in obs:
        return [0, 0]

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Obstacle "pressure": prefer squares with fewer adjacent obstacles (pursuer)
        # and prefer more "escape space" (evader).
        adj = 0
        for ax, ay in adj8:
            if (nx + ax, ny + ay) in obs:
                adj += 1

        dxx, dyy = nx - ox, ny - oy
        dist2 = dxx * dxx + dyy * dyy
        # Heuristic term: pursuer wants small dist2; evader wants large dist2.
        # Add a small tie-break to reduce "free-space trapping".
        if role == "pursuer":
            val = dist2 + 3.0 * adj
            # Tie-breaker: also reduce manhattan, deterministically prefer diagonals.
            man = abs(dxx) + abs(dyy)
            val = val + 0.1 * man
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            val = -dist2 + 3.0 * adj  # larger dist2 -> more negative
            man = abs(dxx) + abs(dyy)
            val = val - 0.1 * man
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]