def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Move toward a corner farther from opponent to maximize collection safety.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda p: cheb(p[0], p[1], ox, oy))
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, target[0], target[1]), cheb(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Interceptor-ish scoring: prefer resources where we are relatively closer than opponent.
    # Then pick move that maximizes our advantage while keeping distance from opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        min_key = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # lower is better: closer to resource, but penalize giving opponent advantage
            key = (d_me - 0.35 * d_opp, d_me, d_opp)
            if min_key is None or key < min_key:
                min_key = key
        # also discourage moving too close to opponent unless it helps interception
        opp_dist = cheb(nx, ny, ox, oy)
        score_tuple = (min_key[0], opp_dist, min_key[1], min_key[2], dx, dy)
        # choose smallest score_tuple lexicographically
        if best_score is None or score_tuple < best_score:
            best_score = score_tuple
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]