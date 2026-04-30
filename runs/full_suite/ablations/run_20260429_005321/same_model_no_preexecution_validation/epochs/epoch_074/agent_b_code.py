def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = {(int(x), int(y)) for x, y in obs}
    resources = [(int(x), int(y)) for x, y in res]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = dx if dx >= 0 else -dx
        dy = ay - by; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy
    def near_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        bestm = (0, 0); bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy) - 0.15 * near_obs(nx, ny)
            if v > bestv:
                bestv = v; bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    # Choose a target resource giving maximal current advantage; then pick move that improves it.
    best_target = None; best_t = -10**18
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Strongly prefer resources we can take immediately; otherwise maximize opponent-distance advantage.
        take = 5.0 if our_d == 0 else 0.0
        v = (opp_d - our_d) + take - 0.06 * (our_d + 0.5 * (abs(rx - cx) + abs(ry - cy)))
        if v > best_t:
            best_t = v; best_target = (rx, ry)
    tx, ty = best_target

    bestm = (0, 0); bestv = -10**18
    cur_our_d = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If we move to/onto the target, prioritize.
        take = 12.0 if our_d == 0 else 0.0
        # Improve advantage; also reduce our distance, and avoid obstacle-adjacency.
        v = take + (opp_d - our_d) - 0.35 * our_d + 0.25 * (cur_our_d - our_d) - 0.18 * near_obs(nx, ny)
        # Mildly avoid giving opponent easier access by heading away if it would reduce their advantage too much.
        opp_adv = (opp_d - cheb(nx, ny, tx, ty))
        v += 0.02 * opp_adv
        # Tie-break: prefer closer to center to keep flexibility.
        v -= 0.03 * cheb(nx, ny, cx, cy)
        if v > bestv:
            bestv = v; bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]