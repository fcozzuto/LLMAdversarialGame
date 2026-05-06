def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    if (sx, sy) in obstacles:
        for yy in range(h):
            for xx in range(w):
                if (xx, yy) not in obstacles:
                    sx, sy = xx, yy
                    break
            else:
                continue
            break

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        best = [0, 0]
        best_s = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            s = dist((nx, ny), opp)  # run away if no targets
            if s > best_s:
                best_s, best = s, [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nxt = (nx, ny)

        # Choose move that maximizes "resource lead" over opponent.
        # lead = (opp_dist - my_dist): positive means we get there earlier.
        my_best = -10**9
        opp_best = 10**9
        for r in resources:
            d_my = dist(nxt, r)
            d_op = dist(opp, r)
            lead = d_op - d_my
            if lead > my_best:
                my_best = lead
            if d_my < opp_best:
                opp_best = d_my

        # Small tie-breaks: prefer being closer to some resource and farther from opponent.
        edge = (nx in (0, w - 1)) or (ny in (0, h - 1))
        score = my_best * 100 + (-opp_best) * 2 + dist(nxt, opp) * 0.15 + (1 if edge else 0) * 0.05

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move