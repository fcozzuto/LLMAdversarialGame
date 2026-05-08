def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pursuer: minimize distance; Evader: maximize distance; tie-breaker by keeping away from nearest obstacle.
    want = -1 if "pursuer" in role else 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        # obstacle proximity penalty
        mind = 10
        for (ax, ay) in obstacles:
            dd = abs(nx - ax) + abs(ny - ay)
            if dd < mind:
                mind = dd
        # score: primary distance (with direction), secondary obstacle clearance (higher mind is better)
        score = want * d + (mind * 0.01)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    # Additional deterministic tie-break: move that changes most towards/away in the dominant axis of relative position.
    if len(moves) > 0:
        dxr = 0 if ox == sx else (1 if ox > sx else -1)
        dyr = 0 if oy == sy else (1 if oy > sy else -1)
        if best != [dxr, dyr] and inb(sx + dxr, sy + dyr):
            # only override if it does not worsen the primary objective for pursuer/evader
            nd = man(sx + dxr, sy + dyr, ox, oy)
            bd = man(sx + best[0], sy + best[1], ox, oy)
            if (want == -1 and nd <= bd) or (want == 1 and nd >= bd):
                best = [dxr, dyr]
    return best