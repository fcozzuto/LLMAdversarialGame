def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = -10**9

    # If no resources, just maximize distance from opponent (avoid being "swept" by pursuit).
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                val = king_dist(nx, ny, ox, oy)
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Precompute whether opponent is "dangerously close" to any resource.
    opp_close = False
    for rx, ry in resources:
        if king_dist(ox, oy, rx, ry) <= 1:
            opp_close = True
            break

    # Move evaluation: aim for resources where we can beat opponent, while keeping safe from opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_adv = -10**9
        best_res_d = 10**9
        for rx, ry in resources:
            ds = king_dist(nx, ny, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            adv = do - ds  # higher is better (we are closer than opponent)
            # Break ties toward nearer resources for faster scoring.
            if adv > best_adv or (adv == best_adv and ds < best_res_d):
                best_adv = adv
                best_res_d = ds

        # Safety term: if opponent is close to resources, prioritize increasing distance from opponent.
        d_op = king_dist(nx, ny, ox, oy)
        safety = d_op if opp_close else (d_op // 2)

        # Also discourage stepping to positions that are simultaneously bad for all resources.
        urgency = -best_res_d

        val = best_adv * 10 + safety * 3 + urgency
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]