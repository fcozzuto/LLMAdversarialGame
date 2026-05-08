def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, step to maximize distance from opponent while staying safe.
    if not resources:
        best = [0, 0]
        bestv = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = d2(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Pick a target resource where we are significantly closer than opponent.
    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        # Prefer resources that opponent is unlikely to deny us: larger (od-sd).
        # Slight preference for nearer-than-average to avoid dithering.
        val = (od - sd) * 1000 - sd
        if best_target is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target

    # Choose the immediate move that reduces distance to the chosen target,
    # but discourages stepping near opponent (denial/contest).
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = d2(nx, ny, rx, ry)
        oppd = d2(nx, ny, ox, oy)
        score = -myd * 10 + oppd
        # If move reaches target, strongly prefer it.
        if nx == rx and ny == ry:
            score += 10**12
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move