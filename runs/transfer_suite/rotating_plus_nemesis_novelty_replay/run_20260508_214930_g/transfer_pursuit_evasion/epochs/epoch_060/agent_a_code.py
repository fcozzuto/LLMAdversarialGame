def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        # Prefer moves that maintain (evader) or reduce (pursuer) distance,
        # and softly penalize stepping near obstacles.
        near_obs = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if (px, py) in obs:
                near_obs += 1

        if is_evader:
            score = dist - 0.15 * near_obs
            better = best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move)
        else:
            score = -dist - 0.15 * near_obs
            better = best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move)

        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]