def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic: move to reduce distance to the closest opponent-visible frontier (roughly toward opponent).
        best = (10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            dopp = dist(nx, ny, ox, oy)
            dself = dist(nx, ny, (w - 1) / 2, (h - 1) / 2)
            cand = (dopp, dself, dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    best_score = -10**18
    best_move = (0, 0)
    center_x, center_y = (w - 1) / 2, (h - 1) / 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Evaluate move by the best resource we could plausibly take next turn.
        move_val = -10**18
        for rx, ry in resources:
            dself = dist(nx, ny, rx, ry)
            dopp = dist(ox, oy, rx, ry)
            # Prefer resources we can beat opponent on, but also deny when they are closer.
            val = (dopp - dself) * 100 - dself
            # Slight tie-break: move toward center to keep options if resources disappear.
            val += -0.01 * (abs(nx - center_x) + abs(ny - center_y))
            if val > move_val:
                move_val = val
        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying put.
        if move_val > best_score or (move_val == best_score and (dx, dy) < best_move):
            best_score = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]