def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
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
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        d_center = abs(nx - cx) + abs(ny - cy)
        d_self = abs(nx - sx) + abs(ny - sy)
        d_opp = abs(nx - ox) + abs(ny - oy)

        if (nx, ny) in unclaimed:
            score = 260 - 2.8 * d_center + 2.0 * d_opp - 0.15 * d_self
        elif (nx, ny) in my_terr:
            score = 60 - 1.6 * d_center + 0.6 * d_opp - 0.08 * d_self
        elif (nx, ny) in op_terr:
            # Flip on entry: go if we can arrive no worse than opponent; otherwise keep pressure away.
            score = 180 - 2.0 * d_center + 2.8 * (d_opp - d_self) + 0.4
        else:
            # Shouldn't usually happen, but treat as mild territory-denial attempt.
            score = 10 - 1.0 * d_center + 0.8 * d_opp - 0.1 * d_self

        # Deterministic tie-break: prefer lower dx, then lower dy, then higher score.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]