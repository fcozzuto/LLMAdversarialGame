def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_t = None
        best_adv = None
        for tx, ty in resources:
            ds = dist2(sx, sy, tx, ty)
            do = dist2(ox, oy, tx, ty)
            adv = do - ds  # prefer where we are closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and (ds < dist2(sx, sy, best_t[0], best_t[1]))):
                best_adv = adv
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None

    # Move greedily toward chosen target, but deterministically break ties by favoring moves
    # that also keep away from obstacles and slightly reduce opponent's ability to intercept.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_next = dist2(nx, ny, tx, ty)
        d_now = dist2(sx, sy, tx, ty)

        # Interception pressure: how close opponent could be next if target is near them.
        do = dist2(ox, oy, tx, ty)

        # Small nudge to avoid moving toward opponent generally (diversify).
        opp_to_me = dist2(nx, ny, ox, oy)

        # Value: primary minimize d_next; secondary prefer increasing our advantage vs opponent.
        my_adv_next = do - d_next
        val = (-d_next, -my_adv_next, opp_to_me, d_now - d_next)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]