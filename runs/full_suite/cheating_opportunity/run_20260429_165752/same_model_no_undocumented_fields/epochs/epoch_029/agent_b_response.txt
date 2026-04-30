def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose the best contested resource: maximize (opp_dist - my_dist), then minimize my_dist.
    best_r = resources[0]
    best_adv = None
    best_my = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - my_d
        if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my) or (adv == best_adv and my_d == best_my and (rx, ry) < best_r):
            best_adv = adv
            best_my = my_d
            best_r = (rx, ry)

    tr, tc = best_r
    best_move = [0, 0]
    best_score = -10**18

    # Deterministic scoring of next move.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_to_t = cheb(nx, ny, tr, tc)
        my_to_o = cheb(nx, ny, ox, oy)

        # Adjacent-to-obstacle penalty to reduce getting wedged.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obstacles:
                    adj_obs += 1

        # Prefer approaching target, keeping some distance from opponent, and avoiding obstacle-adjacent cells.
        score = (-4 * my_to_t) + (1.5 * my_to_o) - (0.75 * adj_obs)

        # Small deterministic tie-breaker: lexicographic order of (dx, dy) after score.
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]