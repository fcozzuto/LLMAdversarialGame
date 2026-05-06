def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            # move away from opponent and slightly toward center for stability
            v = d_opp * 1000 - ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    # Precompute current opponent distances to resources for a "denial" signal
    opp_dists = []
    for rx, ry in resources:
        opp_dists.append(cheb(ox, oy, rx, ry))

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Score favors (1) resources we can reach before opponent from next pos,
        # and (2) reducing opponent's lead on the closest threatenables.
        v = 0
        best_adv = -10**18
        for i, (rx, ry) in enumerate(resources):
            d_self = cheb(nx, ny, rx, ry)
            d_opp = opp_dists[i]
            adv = d_opp - d_self  # positive means we are closer (or equal) than opponent
            # main term: take/contest
            if adv > 0:
                v += (adv * 60) - d_self
            else:
                # denial: reduce their lead especially on near resources
                if d_opp <= 3:
                    v += adv * 25 - d_self
            if adv > best_adv:
                best_adv = adv

        # Encourage making progress toward at least one resource
        # (prevents dithering on negative-adv moves)
        v += best_adv * 10

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]