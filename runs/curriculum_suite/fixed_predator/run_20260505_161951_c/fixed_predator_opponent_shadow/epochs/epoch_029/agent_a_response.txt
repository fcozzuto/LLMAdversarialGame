def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev = min diagonal steps

    def best_target_score(px, py):
        if not resources:
            return None, 0
        best = None
        bestv = None
        for rx, ry in resources:
            sd = dist(px, py, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we reach at least as fast; if tied, prefer ones closer to us.
            # If we are slower, still consider stealing race by penalizing how much slower we are.
            v = (-(od - sd), sd, rx, ry)  # lexicographic min: smallest "urgency gap", then closer
            if bestv is None or v < bestv:
                bestv = v
                best = (rx, ry)
        # transform back to a usable scalar
        return best, bestv[0] * -1

    # If no resources, contest midline by moving to reduce Chebyshev distance to midpoint but avoid being cornered.
    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            d1 = dist(nx, ny, tx, ty)
            d2 = dist(nx, ny, ox, oy)
            v = (d1, -d2, dx, dy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # One-step planning: choose move that maximizes advantage after the move against the best target we would pursue.
    best_pair = None
    bestv = None
    for dx, dy, nx, ny in moves:
        target, _ = best_target_score(nx, ny)
        if target is None:
            v = (-dist(nx, ny, ox, oy), dist(nx, ny, sx, sy), dx, dy)
        else:
            rx, ry = target
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Primary: maximize (od - sd). Secondary: smaller sd. Tertiary: also reduce distance to opponent
            # slightly to discourage them reaching the same contested zone faster.
            v = (-(od - sd), sd, -dist(nx, ny, ox, oy), dx, dy)
        if bestv is None or v < bestv:
            bestv = v
            best_pair = (dx, dy)
    return [best_pair[0], best_pair[1]]