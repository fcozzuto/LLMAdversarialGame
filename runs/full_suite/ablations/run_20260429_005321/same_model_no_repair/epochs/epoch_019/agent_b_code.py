def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        # avoid obstacles when possible
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if (mx == 0 and my == 0) or (inb(nx, ny) and (nx, ny) not in obstacles):
                return [mx, my]
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic tie-break by move order; evaluate all equally-valid moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) != (sx, sy):
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

        # Prefer securing a resource where we can arrive earlier or at least catch up
        best_adv = -10**9
        closest_me = 10**9
        closest_opp = 10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            adv = d_op - d_me  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            if d_me < closest_me:
                closest_me = d_me
            if d_op < closest_opp:
                closest_opp = d_op

        # If we are behind overall, strongly try to reduce the opponent's lead
        behind_pen = (max(0, -best_adv) ** 2)

        # Mild encouragement to reduce our closest resource distance
        me_progress = -closest_me

        # Penalty for being too close to opponent (often increases contest risk)
        opp_dist = max(abs(ox - nx), abs(oy - ny))
        adj_pen = 5 if opp_dist <= 1 else 0
        block_bonus = 0
        # If opponent is closer to many resources, being between them and the nearest resource helps a bit
        if closest_opp < closest_me:
            block_bonus = 3 * (closest_me - closest_opp)

        val = 20 * best_adv + me_progress - behind_pen - adj_pen + block_bonus

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move