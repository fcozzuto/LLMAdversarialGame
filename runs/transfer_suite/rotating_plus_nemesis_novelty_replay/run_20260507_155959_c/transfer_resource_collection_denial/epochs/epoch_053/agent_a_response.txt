def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): 
        dx = x1 - x2; dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    # Predict opponent sweep: they prioritize resources on their current row (y).
    # If none, fall back to nearest-to-opponent overall.
    opp_row = oy
    row_candidates = [r for r in res if r[1] == opp_row]
    if row_candidates:
        target = row_candidates[0]
        best = 10**9; best2 = 10**9
        for rx, ry in row_candidates:
            d = md(ox, oy, rx, ry)
            # Tie-break deterministically: closer first, then farther from us to steal less often? (we want block)
            # Actually we want interception: maximize (our_dist - their_dist negative) -> smaller their_dist, bigger our_dist doesn't help.
            # Use: prefer small (their_dist - our_dist) meaning we can reach no later than them.
            score = d - md(sx, sy, rx, ry)
            if score < best or (score == best and d < best2):
                best = score; best2 = d; target = (rx, ry)
    else:
        target = res[0]
        best = 10**9
        for rx, ry in res:
            score = md(ox, oy, rx, ry) - 2 * md(sx, sy, rx, ry)
            if score < best:
                best = score; target = (rx, ry)

    tx, ty = target
    # Choose a step toward target; if blocked, try alternate.
    best_move = [0, 0]
    best_cost = 10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if abs(dx) > 1 or abs(dy) > 1:
                continue
            # cost: distance to target, then prefer reducing opponent's "row threat"
            cost = md(nx, ny, tx, ty)
            # Small interception term: stay closer to opponent row if target is on it.
            if ty == oy:
                cost += md(nx, ny, ox, oy) // 2
            if cost < best_cost:
                best_cost = cost; best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]