def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    t = observation.get("turns_remaining", 0)
    t = t if isinstance(t, int) else int(t or 0)

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            q = (p[0], p[1])
            if q not in obst:
                resset.add(q)

    if (sx, sy) in resset:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a deterministic target: maximize time advantage for us, then closeness, then lexicographic.
    urgency = 1.0 + (64 - min(64, max(0, t))) / 64.0
    best = None
    best_cmp = None
    for rx, ry in resset:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = (od - sd) * urgency  # stronger commitment late
        cmp = (adv, -sd, -rx, -ry)
        if best is None or cmp > best_cmp:
            best, best_cmp = (rx, ry), cmp

    if best is None:
        # No resources: move to safer/central deterministic step (avoid obstacles).
        targets = [(3, 3), (3, 4), (4, 3), (4, 4)]
        tx, ty = max(targets, key=lambda q: -man(sx, sy, q[0], q[1]))
        best = (tx, ty)

    tx, ty = best

    # Choose among legal deltas; score prefers moving closer to target and away from obstacle cells.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # immediate safety against obstacles
        safety = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obst:
                    safety -= 1
        dist_now = man(sx, sy, tx, ty)
        dist_next = man(nx, ny, tx, ty)
        progress = dist_now - dist_next
        # Also consider not allowing opponent to become strictly better on same target next.
        op_dist_now = man(ox, oy, tx, ty)
        # Opponent can't be controlled; but we can penalize positions where we'd be behind if opponent reaches in same number of steps.
        behind_pen = 0
        if dist_next > op_dist_now:
            behind_pen = (dist_next - op_dist_now) * (1.0 + (1.0 - min(1.0, t / 12.0)))
        score = (progress * 10 + safety * 2 - behind_pen, -man(nx, ny, tx, ty), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move