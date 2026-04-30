def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose a target deterministically: nearest resource; break ties by preferring being closer than opponent.
    target = None
    best_key = None
    for r in resources:
        ds = cheb((sx, sy), r)
        do = cheb((ox, oy), r)
        key = (ds, do - ds, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            target = r
    if target is None:
        # No resources visible: drift toward opponent side while avoiding obstacles.
        target = (w - 1 - sx, h - 1 - sy)

    best = None
    best_move = (0, 0)
    # Heuristic: maximize improvement toward target, while also increasing distance from opponent.
    # If opponent is closer to the target, bias moves that reduce opponent's advantage (increase their distance).
    ds0 = cheb((sx, sy), target)
    do0 = cheb((ox, oy), target)
    opp_adv = 1 if do0 < ds0 else -1  # opponent closer => opp_adv=1 means defend; else opp_adv=-1 means race.

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dst = cheb((nx, ny), target)
        dpo = cheb((nx, ny), (ox, oy))
        dop = cheb((ox, oy), target)
        # Estimated effect: if opponent is close, prioritize moves that increase their remaining distance.
        # We cannot move opponent; use their current advantage and our resulting distance tradeoffs.
        my_gain = ds0 - dst
        opp_def = (dop - cheb((ox, oy), target))  # always 0, but keeps structure stable
        # Practical: use resulting distance to opponent; when opponent is closer, push away from them.
        score = 10 * my_gain + (1.2 if opp_adv == 1 else 0.4) * dpo - (0.15 if opp_adv == 1 else 0.05) * dst
        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]