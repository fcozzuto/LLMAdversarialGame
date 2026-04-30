def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not free(sx, sy):
        for dx, dy in dirs:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    # Pick a target where we are relatively faster than the opponent.
    if resources:
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Larger is better: opponent distance advantage over our distance.
            score = od - sd
            # Prefer immediate/contested-but-win targets.
            key = (score, -sd, -od, tx, ty)
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        tx, ty = best
    else:
        # No resources visible: hold the center-ish direction away from opponent.
        tx, ty = (w // 2, h // 2)
        if cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty):
            tx, ty = (w - 1 - (w // 2), h - 1 - (h // 2))

    # Choose move that best approaches target while not letting opponent gain too much.
    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        # Prefer reducing our distance; also avoid giving opponent an even closer contest state.
        od = cur_od  # opponent position not updated here (engine will update next turn); use current contest.
        improve = cur_sd - sd
        # If multiple, discourage moving into worse "contest" (our lag behind opponent).
        contest = (od - sd)
        # Separation to opponent as a tiebreaker: increasing is good.
        sep = cheb(nx, ny, ox, oy)
        val = (improve, contest, sep, -sd, dx == 0 and dy == 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]