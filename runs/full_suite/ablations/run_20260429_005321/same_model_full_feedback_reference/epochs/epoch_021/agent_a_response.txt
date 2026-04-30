def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def best_opp_next(oxt, oyt, tx, ty):
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = oxt + dx, oyt + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = dist(nx, ny, tx, ty)
                if d < bestd: bestd = d
        return bestd if bestd != 10**9 else dist(oxt, oyt, tx, ty)

    # Pick a contested target: maximize my (op - me) advantage vs distance.
    if resources:
        best_r = resources[0]
        best_adv = -10**9
        for rx, ry in resources:
            adv = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
            if adv > best_adv:
                best_adv, best_r = adv, (rx, ry)
        tx, ty = best_r
    else:
        # No visible resources: move toward center-ish to improve future capture.
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18
    myd0 = dist(sx, sy, tx, ty)
    oppd0 = dist(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd1 = dist(nx, ny, tx, ty)
        # Predict opponent greedy step toward same target.
        oppd1 = best_opp_next(ox, oy, tx, ty)
        # Value: maximize how much I stay ahead; also prefer getting to the target.
        val = (oppd1 - myd1) * 1000 + (oppd0 - myd0) - myd1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]