def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if ok(tx, ty):
                targets.append((tx, ty))
    if not targets:
        tx, ty = w // 2, h // 2
        targets = [(tx, ty)]

    best_move = (0, 0)
    best_val = None

    # Prefer moves that increase advantage to nearest "playable" resource.
    # Deterministic scan order for ties.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # If we can already move onto a resource, that's usually best.
        on_resource = 1 if any(nx == tx and ny == ty for tx, ty in targets) else 0
        # Evaluate best target after this move.
        local = []
        for tx, ty in targets:
            sd = dist(nx, ny, tx, ty)
            od = dist(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer
            # Additional pressure: avoid targets we can't reach quickly.
            time_bias = -sd
            local.append((adv, time_bias, -abs(tx - ox) - abs(ty - oy), tx, ty))
        local.sort(reverse=True)
        adv, time_bias, _, tx, ty = local[0]
        # Overall value: strong for advantage, then pick closest resource, then progress.
        val = (1000 * on_resource) + 10 * adv + time_bias
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]