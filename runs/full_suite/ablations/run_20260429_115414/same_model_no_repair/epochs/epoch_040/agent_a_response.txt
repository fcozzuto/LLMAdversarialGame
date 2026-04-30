def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        best = None
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive: we are closer
            # Tie-break to be deterministic and slightly prefer safer/central resources
            key = (adv, -ds, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry), ds, do)
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        tx, ty = w // 2, h // 2
        best_key = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # One-step lookahead: choose move maximizing next-step advantage, then minimize opponent access.
    cur = best_adv(sx, sy)
    cur_adv = cur[0][0] if cur is not None else -10**9
    best_key = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nxt = best_adv(nx, ny)
        if nxt is None:
            continue
        key_adv, (rx, ry), ds, do = nxt[0], nxt[1], nxt[2], nxt[3]
        # Penalize moves that give opponent a substantially better "best target"
        # by slightly discouraging large (our distance - their distance to same resource).
        # Also reward improvement over current advantage when possible.
        adv_improve = key_adv - cur_adv
        # Central bias to break ties consistently
        center_bias = -cheb(nx, ny, w // 2, h // 2)
        key = (adv_improve, key_adv, -do, -ds, center_bias, -rx, -ry, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]