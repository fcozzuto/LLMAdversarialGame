def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best target by expected advantage (with strong bias to avoid ones opponent is already winning)
    best_r = None
    best_key = None
    for rx, ry in resources:
        if inb(rx, ry):
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = ds - do
            # Lower is better; discourage opponent-first targets
            key = (0 if adv <= 0 else 1, adv, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    # Candidate move evaluation: primary chase (to tx,ty), secondary defense against opponent-first resources.
    best_move = (0, 0)
    best_val = None
    # Precompute up to a few most relevant opponent-threatening targets
    threat = []
    for rx, ry in resources:
        if inb(rx, ry):
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if do <= ds + 1:  # close race / opponent slightly ahead
                threat.append((rx, ry, ds, do))
    threat.sort(key=lambda t: (t[3] - t[2], t[3], t[0], t[1]))
    threat = threat[:3]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_to_target = cheb(nx, ny, tx, ty)
        # Base: minimize distance to our chosen target
        val = my_to_target

        # Adjust: try to reduce worst opponent advantage on nearby threats
        worst = -10**9
        for rx, ry, ds, do in threat:
            n_ds = cheb(nx, ny, rx, ry)
            n_do = cheb(ox, oy, rx, ry)
            # If we become closer than opponent, it's good; otherwise reduce how much worse we are
            score = n_do - n_ds
            if score > worst:
                worst = score
        # larger worst is bad; incorporate strongly
        val = val + 4 * worst

        # Micro-avoid: discourage moving closer to opponent (when not needed)
        dist_opp = cheb(nx, ny, ox, oy)
        val = val - 0.01 * dist_opp

        key = (int(val * 100), nx, ny)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]