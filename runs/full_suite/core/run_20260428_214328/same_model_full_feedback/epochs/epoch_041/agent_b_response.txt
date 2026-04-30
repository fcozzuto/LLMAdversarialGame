def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Opponent nearest resource (used to contest deterministically)
    opp_best_d = 10**9
    opp_best_r = None
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_best_d or (d == opp_best_d and (rx, ry) < (opp_best_r[0], opp_best_r[1]) if opp_best_r else True):
            opp_best_d = d
            opp_best_r = (rx, ry)

    def nearest_self_from(x, y):
        best_d = 10**9
        best_r = None
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < best_d or (d == best_d and (rx, ry) < (best_r[0], best_r[1]) if best_r else True):
                best_d = d
                best_r = (rx, ry)
        return best_d, best_r

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        sd, sr = nearest_self_from(nx, ny)
        # Contest: move closer to opponent's closest resource, but prioritize our own
        contest = -man(nx, ny, opp_best_r[0], opp_best_r[1]) if opp_best_r else 0
        # Safety: keep distance from opponent when tie
        dist_opp = man(nx, ny, ox, oy)

        # Deterministic scoring:
        # primary: reduce distance to nearest resource for us
        # secondary: increase distance from opponent
        # tertiary: contest opponent's nearest resource
        score = (-sd * 1000) + (dist_opp * 10) + contest

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # tie-break deterministically: prefer smallest dx, then dy? (stable)
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]