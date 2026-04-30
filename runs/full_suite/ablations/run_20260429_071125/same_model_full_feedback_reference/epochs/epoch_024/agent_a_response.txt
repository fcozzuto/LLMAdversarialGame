def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
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
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, bias towards center to keep options flexible.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (1e18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - cx) + abs(ny - cy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[1] or best[2] else [0, 0]

    # Deterministic ordering for tie-breaks: by distance moved then dx,dy.
    deltas = sorted(deltas, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    best_move = (None, -1e18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Score resources by advantage after moving: favor my closer access and deny opponent.
        score = 0.0
        mx = nx
        my = ny
        for rx, ry in resources:
            myd = cheb(mx, my, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer resources I can reach no later than opponent; otherwise still consider.
            adv = opd - myd
            # Encourage nearer targets and discourage chasing behind.
            score += (adv * 3.0) - (myd * 0.35) + (1.6 if myd == 0 else 0.0)

        # Slightly discourage getting stuck behind obstacles by penalizing farthest-from-center drift.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= (abs(nx - cx) + abs(ny - cy)) * 0.02

        if score > best_move[1]:
            best_move = ((dx, dy), score)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]