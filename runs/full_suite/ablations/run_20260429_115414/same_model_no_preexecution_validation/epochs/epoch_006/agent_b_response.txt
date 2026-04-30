def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_prox(x, y):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best: best = d
        return best

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = -10**9

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if resources:
        # Evaluate each possible move by how it changes our advantage to the best resource.
        for dx, dy, nx, ny in legal_moves:
            my_obs = obstacle_prox(nx, ny)
            opp_obs = obstacle_prox(ox, oy)
            # Choose the resource that maximizes our margin (opponent distance - our distance).
            best_margin = -10**9
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # prefer finishing closer and avoid resources that opponent is already likely to reach much sooner
                margin = (od - md) * 4 - md
                if md == 0:
                    margin += 1000
                # slight bias against risky proximity to obstacles
                margin -= (2 - my_obs) * 5 if my_obs <= 2 else 0
                # if we're currently worse on this resource, reduce its attractiveness
                cm = cheb(sx, sy, rx, ry)
                om = cheb(ox, oy, rx, ry)
                if cm > om:
                    margin -= 6
                if margin > best_margin:
                    best_margin = margin
            # Additional tie-breakers: don't step into immediate obstacle-adjacent traps; keep away from opponent a bit
            opp_dist = cheb(nx, ny, ox, oy)
            val = best_margin + (opp_dist * 0.5) - (1.5 if my_obs <= 1 else 0) - (0.5 if my_obs == 2 else 0)
            # Deterministic tie-break: prefer smaller (dx,dy) lexicographically after value
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move to center while maximizing distance from opponent and avoiding obstacles.
    tx, ty = (w - 1) // 2, (h - 1) // 2
    for dx, dy, nx, ny in legal_moves:
        my_obs = obstacle_prox(nx, ny)
        center_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)
        val = (-center_d * 3) + (opp_d * 1.2) - (10 if my_obs <= 0 else 0) - (3 if my_obs <= 1 else 0) - (1 if my_obs == 2 else 0)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]