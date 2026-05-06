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

    if resources:
        # Score each move by choosing the resource where we can gain most over the opponent.
        best_move = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            best_res_val = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent, and slightly discourage being near opponent if no lead.
                lead = do - ds
                # Encourage progress: lower ds is better, higher ds is worse when lead small/negative.
                v = lead * 100 - ds
                if best_res_val is None or v > best_res_val:
                    best_res_val = v
            if best_res_val is None:
                best_res_val = -10**9
            if best_val is None or best_res_val > best_val:
                best_val = best_res_val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift to center while keeping some distance from opponent.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_center = cheb(nx, ny, cx, cy)
        dist_opp = cheb(nx, ny, ox, oy)
        v = dist_opp * 2 - dist_center
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]