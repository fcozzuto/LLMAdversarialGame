def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    # Strategic change: target maximizes immediate advantage (opponent dist - our dist).
    best = None
    best_key = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        adv = od - sd
        # If we can likely win the resource, strongly prefer it; otherwise, deny by going where we lose less.
        key = (-adv, sd, -od, x, y)  # deterministic tie-breaks
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    # Move: choose step that brings us closer to target; tie-break by improving advantage and distancing opponent.
    cur_sd = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Advantage after move uses our distance only (opponent position static this turn).
        adv_after = nod - nsd
        opp_dist = cheb(nx, ny, ox, oy)
        mkey = (nsd, -adv_after, -opp_dist, dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # If all moves blocked, stay.
    return [int(best_move[0]), int(best_move[1])]