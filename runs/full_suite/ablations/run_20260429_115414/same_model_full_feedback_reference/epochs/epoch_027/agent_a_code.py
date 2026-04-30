def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        resources = [(tx, ty)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target where we are relatively closer than opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        md = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - md
        # Prefer: high advantage, then low my distance, then top-left tie-break.
        key = (adv, -md, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # If opponent is dramatically closer to our best target, shift to the best among resources where we are closer.
    op_dist = man(ox, oy, tx, ty)
    my_dist = man(sx, sy, tx, ty)
    if op_dist - my_dist >= 3:
        chosen = None
        chosen_key = None
        for rx, ry in resources:
            md = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            if md <= od:
                adv = od - md
                key = (adv, -md, -rx, -ry)
                if chosen_key is None or key > chosen_key:
                    chosen_key = key
                    chosen = (rx, ry)
        if chosen is not None:
            tx, ty = chosen

    # Choose move minimizing our distance to target, while also avoiding moving into opponent proximity.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        od2 = man(nx, ny, ox, oy)
        # Primary: smallest distance to target; Secondary: keep farther from opponent.
        val = (nd, -od2, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]