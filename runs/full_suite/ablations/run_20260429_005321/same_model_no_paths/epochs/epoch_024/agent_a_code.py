def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Pick target by estimated contest advantage: we want to be closer than opponent.
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; if tied, prefer central; always prefer nearer to avoid late races.
        score = (opd - myd) * 50 - myd + (-cheb(rx, ry, cx, cy))
        if best is None or score > best[0]:
            best = (score, rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best[1], best[2]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cur_dist = cheb(sx, sy, tx, ty)

    # Among valid moves, maximize post-move contest (assuming opponent doesn't move), and keep us progressing.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Post-move advantage if we were already at new position.
        opd_to_target = cheb(ox, oy, tx, ty)
        advantage = opd_to_target - nd  # higher is better for us
        # Keep moving toward target; slight preference to move away from opponent to reduce blocking collisions.
        val = advantage * 100 - nd * 2 + cheb(nx, ny, ox, oy) * 0.1
        if best_val is None or val > best_val or (val == best_val and (nd < cur_dist)):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]