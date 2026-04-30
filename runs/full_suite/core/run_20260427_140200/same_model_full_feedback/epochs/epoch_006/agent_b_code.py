def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    rpos = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                rpos.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if (sx, sy) in obs:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [int(dx), int(dy)]
        return [0, 0]

    if not rpos:
        # No resources: drift toward center while avoiding obstacles/opponent proximity slightly
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty) - 0.15 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return [int(best[0]), int(best[1])]

    best_move = [0, 0]
    best_val = -10**18
    # Mild bias to keep deterministic "best" stable
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate move by best "contested" resource
        # Score: (opp_time - self_time) with tie-break by self being closer; add tiny anti-oscillation
        move_best = -10**18
        for rx, ry in rpos:
            sdist = cheb(nx, ny, rx, ry)
            odist = cheb(ox, oy, rx, ry)
            # Prefer resources where we arrive earlier (positive advantage), but still allow contested if close.
            v = (odist - sdist) * 2.0 - sdist * 0.25
            # If we can grab immediately, strongly prefer
            if nx == rx and ny == ry:
                v += 1000.0
            # If opponent can grab immediately, slightly penalize
            if ox == rx and oy == ry:
                v -= 20.0
            if v > move_best:
                move_best = v

        # Small incentive to reduce distance to opponent when tied (avoid being out-logged)
        vfinal = move_best - 0.05 * cheb(nx, ny, ox, oy) + (0.001 if (dx == 0 and dy == 0) else 0.0)
        if vfinal > best_val:
            best_val = vfinal
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]