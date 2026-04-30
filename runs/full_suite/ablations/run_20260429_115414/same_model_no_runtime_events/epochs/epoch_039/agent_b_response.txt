def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem)
    except:
        rem = len(resources)
    late = rem <= 4

    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best_adv = -10**18
        my_best_d = 10**18
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd
            if adv > my_best_adv or (adv == my_best_adv and myd < my_best_d):
                my_best_adv = adv
                my_best_d = myd

        # Late game: bias stronger toward grabbing quickly; otherwise prefer positive advantage.
        score = my_best_adv * (200 if late else 100) - my_best_d
        # If we move onto/adjacent to opponent, reduce risk slightly (no randomness).
        if dist(nx, ny, ox, oy) <= 1:
            score -= 3

        if score > best_score:
            best_score = score
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]