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

    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if ok(rx, ry):
                res_set.add((rx, ry))
    if not res_set:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_score = 0
        collected = 1 if (nx, ny) in res_set else 0
        # For each resource, estimate advantage after making this move.
        # Prefer collecting and maximizing (opp_dist - my_dist).
        best_adv = -10**18
        for rx, ry in res_set:
            ds_new = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds_new
            # Small tie-break toward resources nearer to current position.
            adv -= 0.01 * man(sx, sy, rx, ry)
            if adv > best_adv:
                best_adv = adv
        move_score = collected * 1000 + best_adv
        key = (move_score, -man(nx, ny, sx, sy), -man(nx, ny, ox, oy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]