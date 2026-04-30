def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_val = -10**18

    # Choose target deterministically: minimize (distance to self, + distance to opponent, then coords)
    def pick_target():
        best_t = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (ds, -do, tx, ty)  # prefer close, and prefer targets farther from opponent
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        return best_t

    tx, ty = pick_target()

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_dist = cheb(nx, ny, tx, ty)
        op_dist = cheb(ox, oy, tx, ty)

        # Prefer reducing distance quickly; also avoid letting opponent get too close to our chosen target.
        # Small tie-break: prefer moves with better improvement in both axes.
        my_now = cheb(sx, sy, tx, ty)
        improvement = my_now - my_dist
        tie = -(abs((nx - tx)) + abs((ny - ty)))

        # If we can step onto a resource, strongly prefer it.
        on_res = 1 if (nx, ny) in resources else 0

        val = on_res * 10**6 + improvement * 10**3 + (op_dist - cheb(ox, oy, tx, ty)) * 0 + tie
        # Also add a gentle threat component: avoid moving closer to opponent when not on resource.
        opp_closer = cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)
        val += -opp_closer * 2

        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]