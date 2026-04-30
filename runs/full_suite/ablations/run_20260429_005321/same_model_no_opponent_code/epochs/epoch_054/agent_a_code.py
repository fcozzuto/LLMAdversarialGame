def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy  # squared

    # pick best target by closeness advantage over opponent
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    rx, ry = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        hit = (nx, ny) in obstacles
        # distance to target and also discourage giving opponent immediate closeness
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # slight preference for moving off current obstacle pressure
        obstacle_adj = 0
        for ax, ay in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx-1, ny+1), (nx+1, ny-1), (nx+1, ny+1)]:
            if (ax, ay) in obstacles:
                obstacle_adj += 1
        val = d_self + (0 if not hit else 10**9) + (0.15 * obstacle_adj) - (0.02 * d_opp) + (0.001 * (dx*dx + dy*dy))
        if val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]