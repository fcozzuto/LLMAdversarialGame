def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = max(abs(nx - ox), abs(ny - oy))
                v = d
                if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
                    bestv = v
                    best = [dx, dy]
        return best

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Evaluate resources by who is closer; prefer where we're at an advantage.
    chosen = None
    chosen_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Advantage first, then closeness, deterministic tie-break by coords.
        v = (opd - myd) * 1000 - myd
        if v > chosen_score or (v == chosen_score and (rx, ry) < (chosen[0], chosen[1]) if chosen else True):
            chosen_score = v
            chosen = (rx, ry)

    # Move one step toward chosen; if that makes us worse vs opponent, allow slight evasive step.
    tx, ty = chosen
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        # Additional pressure: prevent opponent from getting adjacent while we chase.
        opp_adj = -cheb(nx, ny, ox, oy)
        v = adv * 1000 - myd + opp_adj
        if v > bestv or (v == bestv and (dx, dy) < tuple(best)):
            bestv = v
            best = [dx, dy]
    return best