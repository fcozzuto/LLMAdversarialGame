def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        # Prefer going toward the corner farthest from opponent (likely last-chance cluster)
        best_move = [0, 0]
        bestv = -10**18
        tx, ty = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best_move = [dx, dy]
        return best_move

    # For each candidate move, consider the best resource race outcome.
    # Value aims to win races (opp_dist - self_dist), with a small bias to reduce self distance.
    best_move = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Compute best contest score among all visible resources
        vbest = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Winning race: od > sd. Add strong weight to that gap, mild to self speed.
            v = (od - sd) * 100 - sd
            # If very close to a resource, prioritize it deterministically
            if sd == 0:
                v += 1000000
            if v > vbest:
                vbest = v
        # Secondary tie-break: prefer progress toward the chosen best resource using manhattan
        if vbest > bestv:
            bestv = vbest
            best_move = [dx, dy]
        elif vbest == bestv:
            # Deterministic tie-break: lower manhattan to opponent-farthest corner
            far_corner = max([(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)],
                              key=lambda c: cheb(c[0], c[1], ox, oy))
            if manh(nx, ny, far_corner[0], far_corner[1]) < manh(sx + best_move[0], sy + best_move[1], far_corner[0], far_corner[1]):
                best_move = [dx, dy]

    return best_move