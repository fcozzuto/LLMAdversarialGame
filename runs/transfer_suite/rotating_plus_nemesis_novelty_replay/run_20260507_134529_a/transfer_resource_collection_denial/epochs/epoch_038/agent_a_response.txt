def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources: block closest potential area by moving toward opponent's row/col centerline
        tx, ty = sx, sy
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = -cheb(nx, ny, ox, oy)
            if v > bestv: bestv, best = v, (dx if free(sx+dx,sy+dy) else 0, dy if free(sx+dx,sy+dy) else 0)
        return [best[0], best[1]]

    # Pick a contested target if possible; else go to nearest resource
    best_target = resources[0]
    best_key = (-10**18, 10**18)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key1 = do - ds  # positive means opponent is farther; we are closer advantage
        key2 = ds
        if key1 > best_key[0] or (key1 == best_key[0] and key2 < best_key[1]):
            best_key = (key1, key2)
            best_target = (rx, ry)

    tx, ty = best_target
    # If everyone looks uncontested, bias to nearest resource; otherwise bias to contested ones
    contested = best_key[0] >= 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        our_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)

        # Main objective: maximize advantage over opponent on the best nearby resources
        # using limited lookahead over the closest few resources.
        scored = 0
        val = 0
        for rx, ry in sorted(resources, key=lambda p: cheb(nx, ny, p[0], p[1]))[:4]:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            # Encourage getting to at least one resource quickly; discourage moves that let opponent get closer first
            val += (adv * 3) - ds
            scored += 1

        # Tactical term: if contested, prioritize reducing our distance to the contested target while not worsening opp disadvantage
        if contested:
            val += (our_to_t * -2) + (opp_to_t - our_to_t) * 1.5
        else:
            val += (our_to_t * -1.5)

        # Small deterministic tie-break: prefer moves that reduce Chebyshev distance to the opponent less
        val += -0.05 * cheb(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = (dx if free(sx+dx, sy+dy) else 0, dy if free(sx+dx, sy+dy) else 0)

    return [best_move[0], best_move[1]]