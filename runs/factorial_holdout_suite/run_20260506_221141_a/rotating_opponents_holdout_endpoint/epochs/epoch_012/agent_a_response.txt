def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                sc = -man(nx, ny, tx, ty)
                if best is None or sc > best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_next = None
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_r_score = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Big preference for resources where we are closer than opponent (denial opponent).
            sc = (do - ds) * 1000 - ds
            if (best_r_score is None) or (sc > best_r_score):
                best_r_score = sc

        # If multiple resources tie, prefer smaller distance (embedded in score); but add tiny bias to speed.
        if best_r_score is None:
            continue
        if best_next is None or best_r_score > best_next[0]:
            best_next = (best_r_score, dxm, dym)

    return [best_next[1], best_next[2]] if best_next else [0, 0]