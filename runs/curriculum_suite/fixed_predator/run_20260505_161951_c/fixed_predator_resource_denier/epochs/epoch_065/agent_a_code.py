def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, just avoid opponent while slightly drifting to center.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_center = abs(nx - tx) + abs(ny - ty)
            v = d_opp * 1000 - d_center
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each move by how much it can beat or deny the best resource.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # For each resource: if we can get there no later than opponent, it's a take;
        # otherwise we try to deny by reducing opponent advantage.
        local_best = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(nx, ny, ox, oy) + cheb(ox, oy, rx, ry) - cheb(nx, ny, ox, oy)
            # The above keeps it lightweight while correlating "opponent after their move".
            # Use simpler correlation if it goes too weird.
            if d_opp < 0:
                d_opp = cheb(ox, oy, rx, ry)

            # Gain: positive means we arrive sooner/tie; negative means we fall behind.
            gain = (d_opp - d_self)
            # Tie-break: prefer closer resources (faster scoring).
            val = gain * 50 - d_self

            # Strongly prefer cells that are at/near a resource the opponent is currently closest to.
            # (Denial pressure.)
            opp_to_res = cheb(ox, oy, rx, ry)
            self_to_res = cheb(x, y, rx, ry)
            if opp_to_res <= self_to_res:
                val += 20

            if val > local_best:
                local_best = val

        # Small penalty for being closer to obstacle choke less is automatic via validity.
        # Encourage not to step adjacent to obstacles (soft).
        adj_obs = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1)]:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                adj_obs += 1
        v = local_best - adj_obs * 3

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]