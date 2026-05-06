def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return (dx * dx + dy * dy) ** 0.5

    if resources:
        # pick a few promising resources deterministically
        scored = []
        for r in resources:
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            # favor close-to-us and far-from-them; tiny tie-break on coords
            key = (ds - 0.35 * do, r[0], r[1])
            scored.append((key, r))
        scored.sort(key=lambda t: t[0])
        targets = [scored[i][1] for i in range(min(3, len(scored)))]

        best = None
        best_score = -1e18
        for dx, dy, nx, ny in valid:
            my_pos = (nx, ny)
            worst_adv = 1e18
            # choose a move that is strong on at least one target but not terrible on others
            for r in targets:
                adv = dist((ox, oy), r) - dist(my_pos, r)
                if adv < worst_adv:
                    worst_adv = adv
            # add slight progress to nearest target
            nearest = min(targets, key=lambda r: dist(my_pos, r))
            prog = -dist(my_pos, nearest)
            score = 2.0 * worst_adv + 0.1 * prog
            if score > best_score + 1e-12:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources visible: move toward center while keeping away from opponent
    center = (w // 2, h // 2)
    best = None
    best_score = -1e18
    for dx, dy, nx, ny in valid:
        my_pos = (nx, ny)
        score = -dist(my_pos, center) - 0.15 * dist(my_pos, (ox, oy))
        if score > best_score + 1e-12:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]