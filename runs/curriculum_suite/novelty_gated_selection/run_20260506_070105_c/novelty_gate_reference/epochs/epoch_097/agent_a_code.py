def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    man = lambda ax, ay, bx, by: abs(ax - bx) + abs(ay - by)
    cheb = lambda ax, ay, bx, by: (abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by))

    # Step 1: if we can grab a resource next, do it (strong deterministic change vs pure targeting).
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    adj = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) in adj:
            return [dx, dy]

    # Step 2: choose target that minimizes opponent's lead while we still advance.
    # Use a blended objective to avoid repeating the earlier single-race bias.
    best_t = None
    best_v = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If opponent is closer, heavily prefer targets where we can reduce/deny their advantage.
        # If we are closer, still prefer faster completion, but less aggressively.
        lead = do - ds
        v = (lead * 14) + (ds * 2) - (do * 3)
        # Secondary: prefer targets on our side directionally (toward opponent is worse).
        v += (sx + sy) * 0.0 + (rx + ry) * 0.0
        if best_v is None or v < best_v:
            best_v, best_t = v, (rx, ry)

    rx, ry = best_t

    # Step 3: pick the move that optimizes the next-step version of the objective.
    best_m = (0, 0)
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Also gently discourage stepping toward cells that are much closer to opponent than to us.
        self_rel = cheb(nx, ny, ox, oy)  # distance between agents from new position
        s = (do - ds) * 14 + ds * 2 - self_rel * 0.6
        if best_s is None or s < best_s:
            best_s, best_m = s, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]