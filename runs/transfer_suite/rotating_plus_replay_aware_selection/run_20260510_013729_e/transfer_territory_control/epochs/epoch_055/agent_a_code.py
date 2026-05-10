def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    cx, cy = (w - 1) // 2, (h - 1) // 2
    res = observation.get("resources") or []
    remaining = observation.get("remaining_resource_count")
    use_res = res and remaining is None or (isinstance(remaining, (int, float)) and remaining > 0)

    if use_res:
        best = None
        for p in res:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                tx, ty = int(p[0]), int(p[1])
                d = abs(tx - sx) + abs(ty - sy)
                if best is None or d < best[0]:
                    best = (d, tx, ty)
        if best:
            tx, ty = best[1], best[2]
        else:
            tx, ty = cx, cy
    else:
        tx, ty = cx, cy

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    best_move = dirs[0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        dist_to_t = abs(tx - nx) + abs(ty - ny)
        dist_to_o = abs(ox - nx) + abs(oy - ny)

        # If opponent is close, prioritize approaching them slightly; otherwise, prioritize target/resources.
        opp_close = 1 if abs(ox - sx) + abs(oy - sy) <= 3 else 0
        score = dist_to_o * (0.25 if opp_close == 0 else -1.0) + dist_to_t
        score = float(score)

        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]