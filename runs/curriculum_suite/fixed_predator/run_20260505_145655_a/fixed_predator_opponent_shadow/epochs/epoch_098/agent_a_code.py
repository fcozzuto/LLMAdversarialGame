def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = man(ox, oy, x, y) - man(ox, oy, nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Deny/contest heuristic:
    # Prefer moves that increase (opp_dist - my_dist) to some resource (i.e., get closer first).
    # Secondary: if tied, prefer moves that reduce opp's best advantage against any resource.
    # Tertiary: prefer reducing my distance to the best resource.
    best_move = (0, 0)
    best_tuple = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        best_adv = -10**9  # max (opp_dist - my_dist)
        best_my_dist = 10**9
        best_opp_adv = -10**9  # max over resources of (opp_dist_from_here - my_dist_from_here)

        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            adv = d_opp - d_me
            if adv > best_adv:
                best_adv = adv
                best_my_dist = d_me

            # For secondary tie-breaking: how much advantage the opponent currently has if I move here.
            # (Lower is better for them; we use -best_opp_adv in comparison)
            opp_adv = d_opp - d_me  # same expression, but we keep best for stability
            if opp_adv > best_opp_adv:
                best_opp_adv = opp_adv

        # Also compute "current loss" if opponent is closer to all resources; encourage breaking that.
        # Loss break measure: max(0, d_me - d_opp) minimized.
        worst_contest = -10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            contest_loss = d_me - d_opp
            if contest_loss < 0:
                contest_loss = 0
            if -contest_loss > worst_contest:
                worst_contest = -contest_loss

        candidate = (best_adv, -best_opp_adv, -best_my_dist, worst_contest)
        if best_tuple is None or candidate > best_tuple:
            best_tuple = candidate
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]