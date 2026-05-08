def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If we're already on a resource, just stay (pickup should be handled by engine).
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2 and (r[0], r[1]) == (sx, sy):
            return [0, 0]

    # Choose move that maximizes "arrival advantage" for a single resource.
    best = (0, 0)
    best_val = None

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            tx, ty = r[0], r[1]
            if inb(tx, ty) and (tx, ty) not in obs:
                res_list.append((tx, ty))

    if not res_list:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Immediate pickup bonus if we step onto a resource
        pickup_bonus = 0
        for tx, ty in res_list:
            if (tx, ty) == (nx, ny):
                pickup_bonus = 1000
                break

        # Evaluate best target for this candidate move
        local_best = None
        for tx, ty in res_list:
            myd = man(nx, ny, tx, ty)
            opd = man(ox, oy, tx, ty)
            # Prefer stealing: larger (opd - myd); then smaller myd; then lexicographic resource coords.
            val = (opd - myd) * 100 - myd
            if local_best is None or val > local_best[0] or (val == local_best[0] and (tx, ty) < local_best[1]):
                local_best = (val, (tx, ty))
        val_total = pickup_bonus + local_best[0]

        # Tie-break: deterministic ordering by move (dx,dy)
        if best_val is None or val_total > best_val or (val_total == best_val and (dx, dy) < best):
            best_val = val_total
            best = (dx, dy)

    return [best[0], best[1]]