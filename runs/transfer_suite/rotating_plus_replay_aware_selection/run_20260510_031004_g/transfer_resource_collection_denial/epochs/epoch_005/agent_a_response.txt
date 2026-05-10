def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target resource: maximize advantage, then minimize our distance, then prefer far from opponent.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd, -od, -abs(tx - ox) - abs(ty - oy), tx, ty)
        if best_key is None or key > best_key:
            best_key, best_t = key, (tx, ty)

    tx, ty = best_t
    res_set = set((int(r[0]), int(r[1])) for r in resources)

    # Evaluate candidate moves: immediate resource > keep/extend distance advantage > move toward target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if (nx, ny) in res_set:
            score = (1, -1, 0, 0, 0)  # winning immediate pickup
        else:
            sd_new = man(nx, ny, tx, ty)
            sd_cur = man(sx, sy, tx, ty)
            od_new = man(ox, oy, nx, ny)
            adv_new = (man(ox, oy, tx, ty) - sd_new)  # relative to target
            # Encourage advancing toward target while not letting opponent gain.
            score = (0, adv_new, -(sd_new), -(adv_new == (man(ox, oy, tx, ty) - sd_cur) and sd_new), -od_new, nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]