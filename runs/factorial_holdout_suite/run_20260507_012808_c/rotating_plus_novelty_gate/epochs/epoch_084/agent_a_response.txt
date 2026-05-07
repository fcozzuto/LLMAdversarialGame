def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If we can’t win any resource (opponent always closer), still contest by maximizing "closest to turning the tables".
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Utility: take the best contested resource from this next position.
        # advantage > 0 means we are closer than opponent; larger is better.
        # Add a small tiebreak for being closer to the chosen resource and away from corners (less likely to stall).
        val_best = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            # Small deterministic shaping terms
            center_bias = -((rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2) * 1e-6
            prefer_near = -sd * 1e-3
            val = adv * 1e3 + prefer_near + center_bias
            if val > val_best:
                val_best = val

        # Prefer moves that also improve overall ability to reach resources (even if none currently advantaged).
        if val_best > best_val or (val_best == best_val and (dx, dy) < best_move):
            best_val = val_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]