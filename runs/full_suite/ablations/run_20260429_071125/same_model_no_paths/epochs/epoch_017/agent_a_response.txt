def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inside(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Deterministic fallback: move toward center if possible, else stay
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if (d, dx, dy) < best:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    best_move = None
    best_score = -10**18
    tie = 0
    # Score: prioritize reducing own distance to "contested" resources
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cur = 10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # If opponent is closer, discourage; otherwise encourage.
            cont = d_self - d_opp
            val = -d_self - (2.0 * cont if d_opp <= d_self else 0.0)  # higher is better
            if val < cur:
                cur = val
        score = cur
        # Prefer immediate capture/arrival
        if score > best_score or (score == best_score and (dx, dy) < (tie, tie)):
            best_score = score
            best_move = [dx, dy]
            tie = dx

    if best_move is None:
        return [0, 0]
    return best_move