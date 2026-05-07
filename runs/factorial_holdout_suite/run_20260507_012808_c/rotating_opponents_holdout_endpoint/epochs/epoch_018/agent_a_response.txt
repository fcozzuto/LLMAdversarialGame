def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # pick best target deterministically
    best_tx, best_ty = resources[0]
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd  # bigger is better
        cb = abs(tx - cx) + abs(ty - cy)
        key = (-(adv), sd, cb, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = tx, ty

    # choose move that improves our competitiveness toward target
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # if opponent is much closer to some resource, intercept by moving toward the most "contested" one
    opp_best = None
    opp_best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd
        key = (-(adv),)  # we want smallest sd-od negative => most contested where od<=sd; but deterministic adjust below
        # compute "threat": opponent advantage over us
        threat = sd - od
        ck = (-threat, man(ox, oy, tx, ty), abs(tx - cx) + abs(ty - cy), tx, ty)
        if opp_best_key is None or ck < opp_best_key:
            opp_best_key = ck
            opp_best = (tx, ty)

    target = (best_tx, best_ty)
    # strategic switch when we are behind on nearest best target by a margin
    if opp_best is not None:
        tx, ty = target
        behind = man(ox, oy, tx, ty) - man(sx, sy, tx, ty)
        if behind > 2:  # opponent clearly closer
            target = opp_best

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)  # opponent stationary for scoring
        adv2 = od2 - sd2
        # also reward moving closer in general to reduce risk of stalling
        base = (-(adv2), sd2, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_val is None or base < best_val:
            best_val = base
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]