def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources or W <= 0 or H <= 0:
        return [0, 0]

    obs_set = set()
    for o in obstacles:
        try:
            x, y = o
            obs_set.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # we want adv large (we are closer)
        key = (-(adv), ds, (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # Local evaluation: move that best increases closeness advantage to the chosen target,
        # and if that target is contested, prefer any safe move that reduces opponent gap.
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        adv2 = do2 - ds2

        # Tie-break: prefer moves that reduce distance to some resource the opponent is unlikely to take.
        min_other = None
        for rx, ry in resources:
            dsx = man(nx, ny, rx, ry)
            dox = man(ox, oy, rx, ry)
            if dox - dsx < adv2 - 1:
                continue
            v = dsx + man(ox, oy, rx, ry) * 0.01
            if min_other is None or v < min_other:
                min_other = v

        key = (-(adv2), ds2, 0 if (min_other is None) else min_other, rx if (tx, ty) else 0, -dx, -dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    # If all moves blocked (should be rare), stay.
    return [int(best_move[0]), int(best_move[1])]