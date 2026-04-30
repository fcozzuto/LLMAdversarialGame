def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2: continue
        try:
            x, y = int(p[0]), int(p[1])
        except: 
            continue
        if inb(x, y): obs.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p is None or len(p) < 2: continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if inb(x, y) and (x, y) not in obs:
            resources.append((x, y))

    if not inb(sx, sy):
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target resource using distance-race advantage (our dist - opponent dist, maximize negative).
    # If we have no resources, head to mid.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Small tie-break to reduce symmetry: prefer lower x then y deterministically.
            key = (ds - do, ds, rx, ry)
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Move greedily toward target while avoiding obstacles; prefer moves that reduce our distance most.
    # If all improving moves are blocked, pick least-bad move (still deterministic).
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): continue
        if (nx, ny) in obs: continue
        ds2 = man(nx, ny, tx, ty)
        # Score: primary minimize distance to target; secondary prefer diagonal/forward; tertiary tie-break.
        diag = 1 if dx != 0 and dy != 0 else 0
        opp_d = man(nx, ny, ox, oy)
        score = (ds2, -diag, opp_d, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]