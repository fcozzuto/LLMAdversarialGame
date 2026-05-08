def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target where we are closer than opponent (or otherwise maximize advantage).
    best_rx, best_ry = resources[0]
    best_key = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # tie-break: prefer more immediate opportunity, then closer distance, then stable order
        key = (do - ds, ds, (rx + 17 * ry) % 1000)
        if key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    # If opponent is closer by a lot, bias toward our nearest resource instead (avoid being denied).
    ds_best = man(sx, sy, best_rx, best_ry)
    do_best = man(ox, oy, best_rx, best_ry)
    if do_best - ds_best >= 4:
        nearest = None
        nearest_ds = 10**18
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            if ds < nearest_ds:
                nearest_ds = ds
                nearest = (rx, ry)
        if nearest is not None:
            best_rx, best_ry = nearest

    tx, ty = best_rx, best_ry

    # Choose move that greedily reduces distance to target; if equal, improve opponent-block chance by
    # moving into cells that would be good for us and bad for them.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ns = man(nx, ny, tx, ty)
        no = man(nx, ny, ox, oy)  # proxy for "becoming a denier" near opponent
        # Also discourage stepping closer to an obstacle-less immediate "grab" for opponent:
        adv = (man(ox, oy, tx, ty) - ns)
        score = (adv * 1000 - ns * 3 + (-no))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]