def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        # Score target as (opp_dist - self_dist), prefer larger. Deterministic tie breaks by coords.
        targets = sorted(resources, key=lambda r: (-(dist2(sx, sy, r[0], r[1]) - dist2(ox, oy, r[0], r[1])), r[0], r[1]))
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Evaluate move by best advantage it can achieve to reachable targets.
            score = -10**18
            for tx, ty in targets[:5]:
                adv = dist2(ox, oy, tx, ty) - dist2(nx, ny, tx, ty)
                # Slightly prefer closer absolute to reduce oscillation.
                score = max(score, (adv * 1000) - (dist2(nx, ny, tx, ty)))
            cand = (score, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is not None:
            return [best[1], best[2]]

    # Fallback: deterministic move that minimizes distance to center, avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cand = (-dist2(nx, ny, cx, cy), dx, dy)
        if best is None or cand > best:
            best = cand
    if best is not None:
        return [best[1], best[2]]

    # If trapped, stay (should be legal if current cell isn't an obstacle).
    if legal(sx, sy):
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [dx, dy]
    return [0, 0]