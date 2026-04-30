def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Pick a target resource where we have advantage over opponent (prefer larger gap)
    best_r = None
    best_adv = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv = adv
            best_ds = ds
            best_r = (rx, ry)

    tx, ty = best_r
    best = (0, 0)
    bestv = -10**18

    # Evaluate local candidate moves: move toward target, prefer reducing distance, also consider opponent pressure
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Also consider nearest resource after the move
        nearest_after = 10**9
        nearest_opp = 10**9
        for rx, ry in resources:
            dsa = cheb(nx, ny, rx, ry)
            if dsa < nearest_after:
                nearest_after = dsa
            doa = cheb(ox, oy, rx, ry)
            if doa < nearest_opp:
                nearest_opp = doa
        # Higher is better
        v = (nearest_opp - nearest_after) * 10 - ds * 2 - do * 0.5
        # Small preference to avoid lingering when target is reachable
        if ds == 0:
            v += 1000
        if (nx, ny) == (ox, oy):
            v -= 50
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]