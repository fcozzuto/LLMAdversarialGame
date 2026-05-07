def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a, b = x1 - x2, y1 - y2
        if a < 0: a = -a
        if b < 0: b = -b
        return a if a > b else b

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose best target for this move; prioritize resources where we have/establish tempo.
        move_score = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: being closer than opponent.
            # Secondary: closer to the resource now.
            # Tertiary: avoid stepping onto/near opponent by slightly preferring safer targets.
            lead = od - sd
            s2o = cheb(nx, ny, ox, oy)
            val = lead * 100 - sd * 3 - s2o
            if val > move_score:
                move_score = val

        # Deterministic tie-breaking: prefer smaller dx, then smaller dy, then higher score.
        if best_score is None or move_score > best_score or (move_score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = move_score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]