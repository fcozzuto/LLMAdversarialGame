def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_from(x, y):
        if resources:
            best = -10**9
            for rx, ry in resources:
                ds = cheb(x, y, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # New emphasis: deny opponent by targeting resources where we are not slower.
                deny = (do - ds)
                # Also reward simply being close to any resource we can realistically contest.
                closeness = -ds
                s = 2.2 * deny + 0.4 * closeness
                if ds <= do:  # explicitly prioritize contestable resources
                    s += 1.0
                best = s if s > best else best
            return best
        # No resources: drift toward center while keeping some distance from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = cheb(int(round(x)), int(round(y)), int(cx), int(cy))
        dist_opp = cheb(x, y, ox, oy)
        return -0.8 * dist_center + 0.25 * dist_opp

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Deterministic tie-break: prefer (0,0) not allowed in list; use lexicographic on dx,dy after score.
    # New behavior: may even stay close to opponent if that increases contest-deny score.
    best_move = None
    best_s = -10**9
    for dx, dy, nx, ny in moves:
        s = score_from(nx, ny)
        if s > best_s:
            best_s = s
            best_move = (dx, dy)
        elif s == best_s:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]