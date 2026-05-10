def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not unclaimed:
        dirs = [d for d in dirs]  # keep deterministic
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            score = (abs(nx - ox) + abs(ny - oy), -abs(nx - sx) - abs(ny - sy))
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best else [0, 0]

    # Consider only up to 20 unclaimed cells closest to current
    unclaimed_sorted = []
    for x, y in unclaimed:
        d = abs(x - sx) + abs(y - sy)
        if len(unclaimed_sorted) < 20:
            unclaimed_sorted.append((d, x, y))
            if len(unclaimed_sorted) == 20:
                unclaimed_sorted.sort(reverse=True)
        else:
            if d < unclaimed_sorted[0][0]:
                unclaimed_sorted[0] = (d, x, y)
                unclaimed_sorted.sort(reverse=True)
    unclaimed_sorted.sort(key=lambda t: t[0])
    targets = [(x, y) for _, x, y in unclaimed_sorted[:20]] if unclaimed_sorted else unclaimed

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        best_to_target = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < best_to_target:
                best_to_target = d
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = (-best_to_target, dist_opp, -abs(nx - sx) - abs(ny - sy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move