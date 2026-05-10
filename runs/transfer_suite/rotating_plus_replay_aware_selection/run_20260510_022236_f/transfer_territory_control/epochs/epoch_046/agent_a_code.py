def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (sx, sy)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    my_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in unclaimed:
            score = 200 - 2.5 * d_center + 3.0 * d_opp - 0.1 * d_self
        elif (nx, ny) in my_terr:
            score = 20 - 1.5 * d_center + 1.0 * d_opp - 0.05 * d_self
        elif (nx, ny) in op_terr:
            # Entering opponent-controlled territory flips control; allow if it's strategically better.
            score = 90 - 2.0 * d_center + 2.0 * d_opp - 0.1 * d_self
        else:
            score = -10 - 1.0 * d_center + 0.5 * d_opp - 0.1 * d_self

        # Tie-break deterministically
        candidates.append((score, -dx, -dy, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]