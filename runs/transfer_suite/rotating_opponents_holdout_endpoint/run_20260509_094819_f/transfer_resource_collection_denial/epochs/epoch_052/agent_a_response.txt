def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(s[0]), int(s[1]), int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        adv = opd - myd
        # Prefer bigger advantage; then closer for us; then deterministic spatial order
        key = (adv, -myd, -(rx + 7 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Candidate moves: 8 directions + stay, deterministic order
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    # Filter within bounds and not into obstacles
    best_move = None
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy toward target, but also consider not getting closer than opponent to that resource
        myd2 = dist((nx, ny), (tx, ty))
        opd2 = dist((ox, oy), (tx, ty))
        # If we can reduce "opponent catch" risk, do it deterministically
        key = (-(myd2), (opd2 - myd2), -(abs(tx - nx) + abs(ty - ny)), (dx, dy))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]