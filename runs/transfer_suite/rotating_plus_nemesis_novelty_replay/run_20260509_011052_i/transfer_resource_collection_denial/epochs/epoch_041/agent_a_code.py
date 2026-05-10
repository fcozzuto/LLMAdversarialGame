def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we're on a resource, just wait (deterministic pickup preference).
    if (sx, sy) in resources:
        return [0, 0]

    best = resources[0]
    best_val = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Prefer targets where we can arrive earlier; otherwise prefer closer resources.
        # Small bias to not let opponent capture: penalize opponent closeness heavily.
        val = (ds - do) * 1000 + ds * 3 - (w + h) + (0 if (x, y) == (sx, sy) else 0) - (do * 10)
        if best_val is None or val < best_val:
            best_val = val
            best = (x, y)

    tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct step (prefer diagonal), then best among 8 neighbors including stay.
    candidates = []
    candidates.append((dx, dy))
    # add axis-aligned variants if diagonal differs
    candidates.append((dx, 0))
    candidates.append((0, dy))
    # also allow slight detours to avoid obstacles
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax == 0 and ay == 0:
                continue
            if ax != dx or ay != dy:
                candidates.append((ax, ay))
    candidates.append((0, 0))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best_move = (0, 0)
    best_score = None
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if not in_bounds(nx, ny):
            continue
        # Score by progress to target and safety vs opponent
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        score = ds2 * 10 + (do2 - ds2) * -5 + (0 if (nx, ny) == (tx, ty) else 1)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]