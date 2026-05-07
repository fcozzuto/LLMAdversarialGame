def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in obstacles_list:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    man = lambda a, b, c, d: abs(a - c) + abs(b - d)

    # Pick best target deterministically by advantage and then closeness/steal.
    best = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # positive if we are closer
        steal_pen = man(sx, sy, rx, ry)  # smaller is better
        # If we are not behind (sd <= od) prioritize heavily.
        if sd <= od:
            key = (adv + 10000, -sd, -rx, -ry)
        else:
            key = (adv, -sd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    rx, ry = best[1], best[2]

    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Try a safe move that reduces our distance to target while keeping advantage.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                pass
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            nsd = man(nx, ny, rx, ry)
            nod = man(ox, oy, rx, ry)
            # Prefer moves that improve advantage; tie-break by closer-to-target then lexicographic.
            advantage = nod - nsd
            moves.append((advantage, -nsd, dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][2]), int(moves[0][3])]