def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # "Materially different": do one-step contest evaluation against all resources,
    # heavily prioritizing resources closer to us than the opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer staying if it doesn't worsen our contest position too much.
        cur_best_adv = -10**18
        cur_our_best = 10**9
        cur_opp_best = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Advantage: positive means we can reach sooner (or tie).
            adv = do - ds

            # Priority term: resources "ahead" toward our side get a slight boost,
            # shifting aim away from symmetrical center wandering.
            # (Assume start corners: our baseline tends to northwest-ish; opponent southeast-ish.)
            side_bias = -(rx + ry)  # smaller x+y is "northwest" in our corner system

            # Also penalize moves that make us far from all resources.
            if ds < cur_our_best:
                cur_our_best = ds
            if do < cur_opp_best:
                cur_opp_best = do

            v = adv * 1000 + (-ds) * 10 + side_bias
            if v > cur_best_adv:
                cur_best_adv = v

        # If opponent has an immediate nearer claim, our move must win the contest on some resource.
        # Tighten by using our closest and opponent closest as secondary signals.
        opp_pressure = (cur_opp_best - cur_our_best) * 5
        tie_break = -abs((nx + ny) - (sx + sy)) * 2  # prefer minimal drift if close

        val = cur_best_adv + opp_pressure + tie_break
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]