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

    rem = observation.get("remaining_resource_count")
    try:
        rem = int(rem)
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose best resource by advantage; in late game favor nearest.
    best = None
    best_key = (-10**18, -10**18)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        if late:
            key = (adv + (10 - myd), -myd)
        else:
            key = (adv, -myd)
        if key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Greedy move toward target with light opponent-pressure; avoid obstacles.
    bestm = (0, 0)
    bestv = 10**18
    for dx0, dy0 in dirs:
        nx, ny = sx + dx0, sy + dy0
        if not (0 <= nx < w and 0 <= ny < h):  # invalid => engine keeps us; treat as very bad
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Lower is better. In late game, reduce my distance strongly.
        v = myd2 + (0.35 if not late else 0.8) * max(0, myd2 - opd2) + (0.02 if late else 0.01) * (abs(nx - tx) + abs(ny - ty))
        if v < bestv:
            bestv = v
            bestm = (dx0, dy0)

    return [int(bestm[0]), int(bestm[1])]