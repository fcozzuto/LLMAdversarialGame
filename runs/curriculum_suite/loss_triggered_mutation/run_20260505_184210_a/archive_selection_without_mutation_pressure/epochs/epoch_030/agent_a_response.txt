def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_lead_cell(px, py):
        # Choose a resource where (opponent distance - my distance) is maximized.
        best = None
        best_v = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            v = (do - ds, -ds, -do)  # primary: lead, tie: closer, then keep opponent farther
            if best_v is None or v > best_v:
                best_v = v
                best = (rx, ry)
        return best, best_v

    # If resources exist, choose move that maximizes our lead at the best resource.
    if resources:
        # Determine the most promising resource from our current position for directionality.
        target, _ = best_lead_cell(sx, sy)
        if target is None:
            return [0, 0]
        tx, ty = target

        best_move = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ds_now = cheb(nx, ny, tx, ty)
            do_target = cheb(ox, oy, tx, ty)
            lead = do_target - ds_now

            # Anti-clump: avoid moving too close to opponent unless it increases lead enough.
            d_opp = cheb(nx, ny, ox, oy)
            safe = d_opp

            # Small preference for moving closer to target.
            progress = -ds_now

            # Combine deterministically (weights tuned for decisive lead changes).
            val = (lead, safe, progress)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

        return [int(best_move[0]), int(best_move[1])]

    # No resources: keep distance and drift toward center-ish corner escape.
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_v = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_opp = cheb(nx, ny, ox, oy)
        d_cent = cheb(nx, ny, cx, cy)
        v = (d_opp, -d_cent)
        if best_v is None or v > best_v:
            best_v = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]