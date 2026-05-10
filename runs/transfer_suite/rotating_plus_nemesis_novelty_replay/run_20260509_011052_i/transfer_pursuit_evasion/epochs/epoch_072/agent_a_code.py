def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_corner_from(px, py, maximize):
        best = None
        bestv = None
        for cx, cy in corners:
            d = cheb(px, py, cx, cy)
            v = d if maximize else -d
            if bestv is None or v > bestv:
                bestv = v
                best = (cx, cy)
        return best

    def legal_moves(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield dx, dy, nx, ny

    # Predict evader tendency: head to its nearest corner.
    predicted_corner = best_corner_from(ox, oy, maximize=False)

    best_move = (0, 0)
    best_score = None

    for dx, dy, nx, ny in legal_moves(sx, sy):
        d_op = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, predicted_corner[0], predicted_corner[1])
        d_corner_opp = cheb(ox, oy, predicted_corner[0], predicted_corner[1])
        # Deterrent to letting opponent move closer unopposed (only informative heuristic).
        d_prev_op = cheb(sx, sy, ox, oy)

        if pursuer:
            score = (-d_op * 2.5) + (-d_corner * 1.2) + (-(d_prev_op - d_op) * 0.8)
            # Encourage forcing opponent away from its predicted corner.
            score += (d_corner_opp * 0.05)
            better = (best_score is None) or (score > best_score)
        else:
            score = (d_op * 2.5) + (-d_corner * 0.8) - ((d_prev_op - d_op) * 0.8)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]