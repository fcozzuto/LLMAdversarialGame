def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in (observation.get("obstacles") or []):
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    start_phase = int(observation.get("turn_index") or 0) % 4
    if start_phase:
        rot = start_phase % len(dirs)
        dirs = dirs[rot:] + dirs[:rot]

    best_move = (0, 0)
    best = None
    opp_adv_weight = 3.0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best target reachable next: prioritize winning contests.
        local_best = None
        for i, (rx, ry) in enumerate(resources):
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can arrive not later than opponent, favor strongly; else discount.
            win_term = 0.0 if ds > do else (10.0 - ds)
            # Encourage moving toward high-impact targets (closer resources).
            val = win_term - opp_adv_weight * max(0, ds - do) - 0.01 * ds - 0.001 * (i % 7)
            if local_best is None or val > local_best:
                local_best = val

        if local_best is None:
            continue
        # Tie-break deterministically: prefer smaller movement distance, then lexicographic.
        md = abs(dx) + abs(dy) - (1 if dx != 0 and dy != 0 else 0)
        key = (local_best, -md, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]