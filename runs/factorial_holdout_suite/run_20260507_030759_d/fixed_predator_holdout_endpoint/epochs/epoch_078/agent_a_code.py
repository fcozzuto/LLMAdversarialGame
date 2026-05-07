def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def target_key(px, py, tx, ty):
        sd = man(px, py, tx, ty)
        od = man(ox, oy, tx, ty)
        return (od - sd, -sd, -((tx + ty) & 1))

    def pick_best_from(px, py):
        best = None
        for tx, ty in resources:
            k = target_key(px, py, tx, ty)
            if best is None or k > best[0]:
                best = (k, (tx, ty))
        return best[1], best[0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer a move that improves "arrive first" advantage, with fallback if blocked.
    target, _ = pick_best_from(sx, sy)
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if target is None:
            score = (0, -man(nx, ny, sx, sy))
        else:
            score = target_key(nx, ny, target[0], target[1])
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # If everything is blocked, stay.
    return best_move