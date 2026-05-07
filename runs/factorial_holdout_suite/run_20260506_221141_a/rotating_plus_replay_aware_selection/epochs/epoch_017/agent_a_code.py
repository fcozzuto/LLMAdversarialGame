def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Prefer moves that secure at least one resource ahead of opponent; otherwise move toward best contest.
    best_move = (0, 0)
    best_score = -10**18

    if not res:
        # Drift toward center while avoiding obstacles
        cx, cy = gw // 2, gh // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                sc = -cheb(nx, ny, cx, cy)
                if sc > best_score:
                    best_score = sc
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Tie-break: deterministic ordering by fixed move list; update only on strictly greater score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_best_gap = -10**9  # max(opp_dist - my_dist)
        my_min_my_dist = 10**9  # min my_dist
        opp_min_opp_dist = 10**9  # min opp_dist to same resource set

        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            gap = opp_d - my_d
            if gap > my_best_gap:
                my_best_gap = gap
            if my_d < my_min_my_dist:
                my_min_my_dist = my_d
            if opp_d < opp_min_opp_dist:
                opp_min_opp_dist = opp_d

        # Score components:
        # 1) Primary: how much closer we are than opponent to some resource (gap)
        # 2) Secondary: smaller distance to our best candidate (implicitly via my_min_my_dist)
        # 3) Tertiary: avoid moves where opponent is universally much closer (opp_min_opp_dist)
        # 4) Slight bonus if we step onto a resource
        on_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in res) else 0

        # Use squared shaping for gap without heavy computation
        gap = my_best_gap
        sc = 0
        if gap >= 0:
            sc = 2000 * gap - 50 * my_min_my_dist + 5 * on_resource
        else:
            sc = -1200 * (-gap) - 30 * my_min_my_dist + 0.5 * opp_min_opp_dist + 2 * on_resource

        # Nudge away from obstacles by penalizing adjacency (local safety)
        # Deterministic and cheap: check 4-neighborhood for blocked
        adj_block = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = nx + ax, ny + ay
            if not in_bounds(xx, yy) or (xx, yy) in obstacles:
                adj_block += 1
        sc -= 5 * adj_block

        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]