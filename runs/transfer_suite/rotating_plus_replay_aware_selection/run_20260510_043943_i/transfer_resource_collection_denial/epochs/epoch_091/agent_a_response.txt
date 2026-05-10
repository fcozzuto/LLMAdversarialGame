def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    targets = []
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not ok(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; tie-break by being closer to us.
        gap = do - ds
        if gap > -10**9:
            targets.append((gap, -ds, rx, ry))
    if not targets:
        return [0, 0]

    targets.sort(reverse=True)
    best_gap, _, tx, ty = targets[0]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Primary: immediate advantage on chosen target
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        score = (od - sd) * 1000 - sd
        # Secondary: if target blocked/less advantageous, consider best alternative quickly
        if score <= best_score - 1:
            # Evaluate only a couple of top targets for robustness
            for k in range(min(3, len(targets))):
                _, _, ax, ay = targets[k]
                s2 = man(nx, ny, ax, ay)
                o2 = man(ox, oy, ax, ay)
                score = max(score, (o2 - s2) * 1000 - s2)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]