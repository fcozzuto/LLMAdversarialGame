def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c; dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    scores = observation.get("scores", None)
    self_score = opp_score = 0
    if isinstance(scores, dict):
        self_score = scores.get(observation.get("self_name", ""), 0)
        opp_score = scores.get(observation.get("opponent_name", ""), 0)
    elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
        self_score, opp_score = scores[0], scores[1]
    behind = (self_score < opp_score)

    best = None  # (priority, resx, resy)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Priority: if behind, prefer resources we're relatively closer to than opponent.
        # If ahead, still prefer our closests but slightly avoid giving opponent easy grabs.
        gap = do - ds
        pr = (gap, -ds) if behind else (-ds, gap)
        if best is None or pr > best[0]:
            best = (pr, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h: 
            return False
        return (nx, ny) not in obstacles

    bestm = None  # (dist_to_target, tie, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Tie-break: deterministic preference to move toward lower dx then lower dy? keep consistent.
        tie = (dx, dy)
        cand = (-dist, (-tie[0], -tie[1]), dx, dy)  # maximize -dist then maximize deterministic tie
        if bestm is None or cand > bestm:
            bestm = cand
    if bestm is None:
        return [0, 0]
    return [bestm[2], bestm[3]]