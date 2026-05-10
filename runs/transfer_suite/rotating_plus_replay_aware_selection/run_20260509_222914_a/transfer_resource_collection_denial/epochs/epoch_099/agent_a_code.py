def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_score = None
    best_move = (0, 0)
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        step = 1 if dxm != 0 or dym != 0 else 0
        # Evaluate by best attainable resource: prefer taking where we are not slower than opponent,
        # and prefer smaller self distance; tie-break deterministically.
        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Larger is better: being ahead matters more than exact distance.
            ahead = do - ds  # positive => we are closer or equally close
            score = ahead * 1000 - ds * 3 - (rx + 7 * ry) * 0.0001
            # Add small preference to finish sooner if we step onto the resource
            if ds == 0:
                score += 100000
            # Deterministic selection
            if local_best is None or score > local_best[0] or (score == local_best[0] and (rx, ry) < local_best[1]):
                local_best = (score, (rx, ry))

        if local_best is None:
            continue
        # Prefer non-staying moves when equally good, but deterministically.
        if best_score is None or local_best[0] > best_score or (local_local := local_best[0]) == best_score and step < (1 if best_move != (0, 0) else 0):
            best_score = local_best[0]
            best_move = (dxm, dym)
        elif best_score is not None and local_best[0] == best_score:
            # Tie-break by move lexicographic for determinism
            if (dxm, dym) < best_move:
                best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]