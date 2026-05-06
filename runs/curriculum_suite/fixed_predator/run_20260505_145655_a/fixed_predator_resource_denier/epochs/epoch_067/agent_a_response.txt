def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose denial target: maximize (opp_dist - self_dist), tie-break by smaller opp_dist, then center.
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        denom = (od - sd)
        center_bias = -(((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0)) * 1e-4)
        cand = (denom, -od, -sd, center_bias, rx, ry)
        if best is None or cand > best:
            best = cand
    tx, ty = best[4], best[5]

    # Evaluate next moves with obstacle avoidance; prefer improving denial and progress to target.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        sd_next = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        denial_gain = (od - sd_next)

        # Small secondary: avoid letting opponent become closer than us to the target.
        opp_ahead_pen = 0
        if man(ox, oy, tx, ty) < sd_next:
            opp_ahead_pen = 1.5

        # Micro: keep moving rather than oscillating at equal distances.
        center_progress = -(((nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0)) * 1e-5)

        score = (denial_gain * 10.0) - (sd_next * 1.0) + center_progress - opp_ahead_pen + (1.0 if (dx != 0 or dy != 0) else 0.0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move