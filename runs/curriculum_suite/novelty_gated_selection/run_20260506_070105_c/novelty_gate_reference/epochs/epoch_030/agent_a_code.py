def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Evaluate each move by best target resource
    best = None
    best_score = None
    ties = 0

    # Precompute current "best advantage" over all resources
    cur_best_adv = -10**9
    cur_best_oppdist = -10**9
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd0 = md(sx, sy, rx, ry)
        od0 = md(ox, oy, rx, ry)
        adv0 = od0 - sd0
        if adv0 > cur_best_adv:
            cur_best_adv = adv0
            cur_best_oppdist = od0

    # If we are behind everywhere, switch: maximize opponent distance while still progressing
    behind_everywhere = cur_best_adv < 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score move by targeting the best resource for us after moving
        move_best_adv = -10**9
        move_best_oppdist = -10**9
        move_best_sd = 10**9
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if adv > move_best_adv or (adv == move_best_adv and od > move_best_oppdist) or (adv == move_best_adv and od == move_best_oppdist and sd < move_best_sd):
                move_best_adv = adv
                move_best_oppdist = od
                move_best_sd = sd

        # Additional opponent proximity penalty to avoid being "safe collected"
        opp_prox = md(nx, ny, ox, oy)

        # Main score: prefer positive advantage; also prefer reaching nearer targets
        # Use squared advantage to break ties more decisively
        if behind_everywhere:
            # If behind everywhere, pick move that increases opponent distance while keeping some progress
            # target_progress: negative sd (larger is better)
            target_progress = -move_best_sd
            score = (move_best_adv + 2) * (move_best_adv + 2) - 0.7 * opp_prox + 0.15 * target_progress
        else:
            score = (move_best_adv + 2) * (move_best_adv + 2) - 0.35 * opp_prox - 0.05 * move_best_sd

        key = (int(score * 1000), -opp_prox, move_best_sd, dx, dy)
        if best is None or key > best:
            best = key
            best_score = score

    if best is None:
        return [0, 0]
    return [best[3], best[4]]