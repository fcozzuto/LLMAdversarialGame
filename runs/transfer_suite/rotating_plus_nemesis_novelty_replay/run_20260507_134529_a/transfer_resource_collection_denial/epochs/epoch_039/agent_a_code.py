def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If stuck with no resources, just drift away from opponent.
    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate moves by a deterministic contest heuristic across resources.
    best_move = (0, 0)
    best_val = -10**18
    # Limit evaluation to a few best resources by current contest.
    scored = []
    for rx, ry in resources:
        ds0 = cheb(sx, sy, rx, ry)
        do0 = cheb(ox, oy, rx, ry)
        scored.append((do0 - ds0, -ds0, rx, ry))
    scored.sort(reverse=True)
    top = scored[:min(4, len(scored))]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        val = 0
        for adv0, negds0, rx, ry in top:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer moves that improve our contest vs opponent; push to finish closer.
            # adv positive => we are closer than opponent for this resource.
            adv = do - ds
            val += (adv * 80) - ds
            # If we are already closer than opponent, add a stronger finish incentive.
            if adv > 0:
                val += 40
            # Slightly penalize moving away from currently best resource by cheb progress.
            val += (adv0 * 5)
        # Small tie-break to reduce oscillation: keep stable unless tied.
        val += -cheb(nx, ny, sx, sy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]