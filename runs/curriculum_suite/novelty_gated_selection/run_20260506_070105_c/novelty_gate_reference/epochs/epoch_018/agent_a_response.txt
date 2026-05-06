def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry):
                edge = (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1)
                ds = dist(sx, sy, rx, ry)
                do = dist(ox, oy, rx, ry)
                if do <= ds:
                    continue
                # Want to be closer than opponent, preferably by a margin; also prefer closer resources.
                score = (do - ds) * 100 - ds + (5 if edge else 0) - (abs(rx - ox) + abs(ry - oy)) * 0.05
                targets.append((score, rx, ry))
    targets.sort(reverse=True)
    if targets:
        _, tx, ty = targets[0]
    else:
        # Fallback: chase nearest reachable resource
        reachable = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if inb(rx, ry):
                    reachable.append((dist(sx, sy, rx, ry), rx, ry))
        reachable.sort()
        if not reachable:
            return [0, 0]
        _, tx, ty = reachable[0]

    # Choose best immediate move by resulting resource advantage
    best = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Compute advantage to target; discourage moving into opponent vicinity when not necessary
        ds2 = dist(nx, ny, tx, ty)
        dt = dist(sx, sy, tx, ty)
        do2 = dist(nx, ny, ox, oy)
        opp_pen = 12 if do2 <= 1 else (2 if do2 <= 2 else 0)
        # Small preference to keep progress: reward reduction in distance to chosen target
        prog = dt - ds2
        val = (1000 - ds2 * 2) + prog * 10 - opp_pen
        # If target is aligned, encourage diagonal/forward steps
        if (dx != 0 and dy != 0) and (tx != sx and ty != sy):
            val += 1
        # Deterministic tie-breaker: lower dx, then lower dy magnitude ordering
        tb = (abs(dx), abs(dy), dx, dy)
        if best is None or val > best or (val == best and tb < best):
            best = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]