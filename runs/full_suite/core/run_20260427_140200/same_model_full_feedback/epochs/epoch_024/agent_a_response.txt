def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Deterministic fallback: drift toward center to reduce distance races
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = cheb(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Pick a target resource that we can reach at least as well as the opponent; otherwise contest closest.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage ds <= do; strongly penalize cases where opponent is much closer.
        key = (0 if ds <= do else 1, (do - ds), -ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target

    # Evaluate moves by improving our distance while also increasing opponent distance to the same target.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        # If move is more direct toward target, reward; if it worsens our path, penalize.
        # Also add a small tie-breaker to avoid wasting time near obstacles by preferring moves that
        # do not increase distance to opponent (helps prevent opponent capture races).
        opp_ds = cheb(nx, ny, ox, oy)
        score = (do2 - ds2) * 100 - ds2 * 3 - opp_ds
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move