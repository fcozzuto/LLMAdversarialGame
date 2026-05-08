def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (0 <= x < w and 0 <= y < h and (x, y) not in blocks):
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocks:
                    targets.append((x, y))

    if targets:
        cx, cy = min(targets, key=lambda t: (t[0] - sx) * (t[0] - sx) + (t[1] - sy) * (t[1] - sy))
    else:
        cx, cy = (w // 2, h // 2)

    best = (0, 0)
    best_score = -10**18
    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocks:
            continue
        dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        oppd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -dist + 0.02 * oppd
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]