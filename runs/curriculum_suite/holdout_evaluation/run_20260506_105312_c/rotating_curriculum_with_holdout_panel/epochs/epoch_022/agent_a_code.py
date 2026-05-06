def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None

    # Choose the resource we're (most) closer to than the opponent (likely not what they take).
    best_r = None
    best_r_val = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = opd - myd
        if val > best_r_val:
            best_r_val = val
            best_r = (rx, ry)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        move_max_diff = -10**9
        move_min_myd = 10**9

        # Evaluate a small set around our chosen target and also nearby contenders.
        cand = []
        if best_r is not None:
            cand.append(best_r)
        # Add up to 3 closest resources to our current position for robustness.
        # Deterministic: sort by (myd, rx, ry).
        nearest = sorted(((cheb(sx, sy, rx, ry), rx, ry) for rx, ry in resources), key=lambda t: (t[0], t[1], t[2]))
        for i in range(min(3, len(nearest))):
            _, rx, ry = nearest[i]
            cand.append((rx, ry))

        used = set()
        for rx, ry in cand:
            if (rx, ry) in used:
                continue
            used.add((rx, ry))
            myd_next = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd_next
            if diff > move_max_diff:
                move_max_diff = diff
            if myd_next < move_min_myd:
                move_min_myd = myd_next

        # Prefer biggest advantage; then smaller remaining distance; then deterministic preference order.
        key = (move_max_diff, -move_min_myd, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]