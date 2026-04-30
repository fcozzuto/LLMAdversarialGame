def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    res = set((p[0], p[1]) for p in resources)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        # Go toward the center deterministically
        tx, ty = (W // 2), (H // 2)
        best = (0, 0, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): nx, ny = sx, sy
            d = cheb(nx, ny, tx, ty)
            score = -d
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    best_dx = 0; best_dy = 0; best_score = -10**18
    # Precompute opponent one-step reachable positions
    opp_next = []
    for ddx, ddy in moves:
        nx, ny = ox + ddx, oy + ddy
        if not legal(nx, ny): nx, ny = ox, oy
        opp_next.append((nx, ny))
    opp_next = list(dict.fromkeys(opp_next))

    # Favors: taking resources immediately, then improving distance advantage vs opponent,
    # then reducing our distance to the closest resource, while discouraging moving adjacent to opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): nx, ny = sx, sy

        immediate = 1 if (nx, ny) in res else 0

        # Distance advantage to best contested resource
        our_best = 10**9
        opp_best = 10**9
        adv_best = -10**9
        closeness = 10**9
        for rx, ry in resources:
            do = cheb(nx, ny, rx, ry)
            dm = cheb(ox, oy, rx, ry)
            if do < our_best: our_best = do
            if dm < opp_best: opp_best = dm
            adv = dm - do
            if adv > adv_best: adv_best = adv
            if do < closeness: closeness = do

        # Penalty if moving into squares opponent could also take next (proxy via overlap)
        overlap_pen = 0
        if (nx, ny) in opp_next:
            overlap_pen = 6

        # Discourage getting too close to opponent unless we can immediately take a resource
        opp_close = cheb(nx, ny, ox, oy)
        opp_pen = 0
        if immediate == 0:
            if opp_close <= 1:
                opp_pen = 8
            elif opp_close == 2:
                opp_pen = 3

        # Score composition
        score = 0
        score += 2000 * immediate
        score += 80 * adv_best
        score += 10 * (6 - closeness)  # prefer closer
        score += 2 * (opp_best - our_best)  # general lead
        score -= overlap_pen + opp_pen

        if score > best_score:
            best_score = score
            best_dx = dx; best_dy = dy

    return [int(best_dx), int(best_dy)]