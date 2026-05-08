def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Targeting policy shift: strongly prefer resources where we are clearly closer.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # If we can "claim" it first, boost heavily; otherwise, still pick the least losing option.
        claim_bonus = 500 if ds < do else (0 if ds == do else -300)
        # Also prefer nearer targets overall to reduce dithering.
        score = (do - ds) * 120 + claim_bonus - ds * 8 + (rx + ry) * 0
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    # Choose step deterministically toward target while avoiding obstacles if possible.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer the direct-sign move; otherwise best progress.
    direct = (dx, dy)
    best = (0, 0)
    best_m = -10**18
    for mdx, mdy in deltas:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < observation["grid_width"] and 0 <= ny < observation["grid_height"] and (nx, ny) not in obstacles:
            prog = -cheb(nx, ny, tx, ty) - cheb(nx, ny, ox, oy) * 0.05
            bonus = 40 if (mdx, mdy) == direct else 0
            if prog + bonus > best_m:
                best_m = prog + bonus
                best = (mdx, mdy)

    return [best[0], best[1]]