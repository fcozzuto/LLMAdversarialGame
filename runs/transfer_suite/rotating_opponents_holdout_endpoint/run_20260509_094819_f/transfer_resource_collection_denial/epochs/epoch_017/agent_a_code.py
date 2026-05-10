def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry):
                ds = man(sx, sy, rx, ry)
                do = man(ox, oy, rx, ry)
                valid_res.append((do - ds, -ds, rx, ry, do, ds))
    if not valid_res:
        return [0, 0]

    valid_res.sort(reverse=True)
    # Primary: best swing (opponent distance - our distance). Secondary: closer to us.
    _, _, tx, ty, do0, ds0 = valid_res[0]

    # Denial: if opponent can win this resource by margin, target a resource they are also likely to lose.
    target = (tx, ty)
    if len(valid_res) > 1:
        # If opponent is significantly closer (or we are likely to lose), pick resource maximizing our arrival advantage with additional tie-break.
        cur_best = valid_res[0]
        opp_margin = cur_best[4] - cur_best[5]  # do - ds
        if opp_margin <= -2:  # opponent closer by at least 2
            best = None
            for adv, nds, rx, ry, do, ds in valid_res[:6]:
                # Want to be at least competitive and make it hard for opponent (do - ds large). Also slightly prefer cells closer to opponent than us.
                sc = (do - ds, -(ds + 0.2 * man(ox, oy, rx, ry)))
                if best is None or sc > best[0]:
                    best = (sc, rx, ry)
            if best is not None:
                target = (best[1], best[2])

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try straight/diagonal move; if blocked, pick best among 8 neighbors + stay using same heuristic.
    steps = [(dx, dy)]
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            if ax == 0 and ay == 0:
                continue
            steps.append((ax, ay))
    steps.append((0, 0))

    best_move = (0, 0)
    best_val = None
    for mx, my in steps:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        # Score neighbor by progress to target and (if available) progress vs opponent on their likely nearest remaining.
        d_to_t = man(nx, ny, tx, ty)
        d_self = man(nx, ny, tx, ty)
        # Find opponent nearest among resources (cheap: consider up to 4 closest by manhattan from opponent)
        opp_near = None
        for adv, nds, rx, ry, do, ds in valid_res[:12]:
            if opp_near is None or do < opp_near[0]:
                opp_near = (do, rx, ry)
        block_term = 0
        if opp_near is not None:
            do, rx, ry = opp_near
            block_term = (do - man(nx, ny, rx, ry))  # larger means harder for opponent
        val = (-d_to_t, block_term, -man(nx, ny, ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]