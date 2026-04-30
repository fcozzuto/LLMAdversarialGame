def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_penalty(x, y):
        p = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                p += 1
        return p

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Fallback: move toward a corner farther from opponent to reduce their access
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = None
        for dx, dy, nx, ny in legal:
            score = cheb(nx, ny, target[0], target[1]) + 0.1 * obst_penalty(nx, ny)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick a resource where we can get closer than the opponent, while not stepping into dangerous obstacle adjacency.
    best_res = None
    best_res_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; also slightly prefer those that are closer to us overall.
        res_score = (ds - do) + 0.05 * ds
        if best_res_score is None or res_score < best_res_score or (res_score == best_res_score and (rx, ry) < best_res):
            best_res_score = res_score
            best_res = (rx, ry)

    rx, ry = best_res

    # Choose the move that improves our distance to the chosen resource and keeps opponent relatively far.
    best = None
    for dx, dy, nx, ny in legal:
        ds = cheb(nx, ny, rx, ry)
        # Opponent "response": approximate by how close opponent would be to the same resource from current position.
        do = cheb(ox, oy, rx, ry)
        # Strongly prioritize minimizing ds, then maximizing (do - ds) (i.e., our advantage), then safety.
        advantage = do - ds
        score = (ds * 10.0) + (-advantage * 2.0) + 0.1 * obst_penalty(nx, ny)
        # Deterministic tie-breaker by move order
        move_key = (dx, dy, nx, ny)
        if best is None or score < best[0] or (score == best[0] and move_key < best[1]):
            best = (score, move_key, dx, dy)

    return [best[2], best[3]]