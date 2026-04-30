def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    if not resources:
        return [0, 0]
    if (sx, sy) in set((r[0], r[1]) for r in resources):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = [(r[0], r[1]) for r in resources]
    target_rank = []
    for rx, ry in res:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where opponent is farther (so we can likely reach first). If tie, pick nearer.
        key = (od - md, -md, -(rx + ry), rx, ry)
        target_rank.append((key, (rx, ry)))
    target_rank.sort(reverse=True)
    # Use top K targets deterministically
    top_targets = [p for _, p in target_rank[:3]]

    best_move = (0, 0)
    best_score = None
    # Evaluate moves by their effect on "winning a target"
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # If moving onto a resource, strongly prioritize
        immediate = 1 if (nx, ny) in set(res) else 0
        if immediate:
            score = (10**6, 0, 0, 0)
        else:
            my_best = 10**9
            opp_best = 10**9
            for rx, ry in top_targets:
                my_best = min(my_best, cheb(nx, ny, rx, ry))
                opp_best = min(opp_best, cheb(ox, oy, rx, ry))
            # Higher is better: we want opp_best - my_best large, and my_best small.
            score = (opp_best - my_best, -my_best, -((nx + ny) % 7), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]