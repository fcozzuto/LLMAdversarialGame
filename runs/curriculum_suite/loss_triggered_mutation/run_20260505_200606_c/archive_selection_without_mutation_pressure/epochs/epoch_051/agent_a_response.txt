def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Deny/claim heuristic: maximize advantage over opponent for the same resource,
        # with a small preference for distancing from the opponent.
        val = 0
        opp_dist_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Core: choose resource where we are relatively closer than opponent.
            val_r = (do - ds) * 10
            # Prefer nearer target overall to convert advantage into collection.
            val_r -= ds
            # Keep some pressure to target resources the opponent could reach soon.
            if do < opp_dist_best:
                opp_dist_best = do
            if do <= ds:
                val_r += 3  # slight bonus for preventing opponent from being strictly closer
            val += val_r

        # Distance shaping: edge_patrol tends to pressure along edges; avoid getting adjacent.
        val -= cheb(nx, ny, ox, oy) * 2

        # Also bias toward resources that opponent is closest to (to deny them specifically).
        for rx, ry in resources:
            do = cheb(ox, oy, rx, ry)
            if do == opp_dist_best:
                ds = cheb(nx, ny, rx, ry)
                val += (opp_dist_best - ds) * 3
                break

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]