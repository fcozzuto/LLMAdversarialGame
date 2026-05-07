def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    raw_obs = observation.get("obstacles") or []
    obstacles = set()
    for p in raw_obs:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    # immediate pickup preference
    res_set = set(res)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0, -10**9)  # dx,dy,score

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        pickup = 1 if (nx, ny) in res_set else 0
        best_target = None
        best_margin = -10**9
        best_ours = 10**9

        # choose target that we can beat the opponent for (cheb steps)
        for rx, ry in res:
            ours = cheb(nx, ny, rx, ry)
            opp = cheb(ox, oy, rx, ry)
            margin = opp - ours  # positive means we are closer/equal
            # tie-break: fewer our steps
            if margin > best_margin or (margin == best_margin and ours < best_ours):
                best_margin = margin
                best_ours = ours
                best_target = (rx, ry)

        tx, ty = best_target
        our_to_target = cheb(nx, ny, tx, ty)
        opp_to_target = cheb(ox, oy, tx, ty)
        margin = opp_to_target - our_to_target

        # Encourage blocking: reduce opponent lead, and avoid being far when chasing
        # Also strongly favor immediate pickup
        score = pickup * 1000000 + margin * 2000 - our_to_target * 3
        if score > best[2]:
            best = (dx, dy, score)

    return [best[0], best[1]]