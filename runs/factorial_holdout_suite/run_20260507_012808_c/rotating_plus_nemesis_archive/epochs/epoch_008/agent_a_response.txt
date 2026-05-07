def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    best_dx, best_dy = 0, 0
    best_key = (-10**18, 10**18, 10**18, 0)  # (adv, myd, rx-ry, tie)

    # Deterministic lexicographic tie via resource order and move index
    move_idx = 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            move_idx += 1
            continue

        # Choose the resource that best swings race in our favor from (nx, ny)
        local_best = (-10**18, 10**18, 10**18)  # (adv, myd, rx+ry)
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            tkey = (adv, myd, rx + ry)
            if tkey > local_best:
                local_best = tkey

        adv, myd, rsum = local_best
        key = (adv, -myd, -rsum, -move_idx)  # maximize adv, minimize myd/rsum; deterministic
        # Convert to a single comparable key that preserves priority
        cmp_key = (adv, -myd, -rsum, -move_idx)
        if cmp_key > best_key:
            best_key = cmp_key
            best_dx, best_dy = dx, dy
        move_idx += 1

    return [int(best_dx), int(best_dy)]