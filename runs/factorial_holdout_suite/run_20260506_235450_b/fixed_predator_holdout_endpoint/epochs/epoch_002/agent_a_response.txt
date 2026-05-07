def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Drift to center, but avoid moving into opponent direction if possible
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        opts = [(-dx, -dy), (dx, dy), (dx, 0), (0, dy), (0, 0)]
        for ddx, ddy in opts:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    # Select a contested target deterministically: maximize (opp_dist - self_dist), then prefer shorter self_dist
    best_t = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (do - ds, -ds, rx, ry)  # higher do-ds better; deterministic tie by coordinates
        if best_t is None or key > best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    # If opponent is clearly closer to everything, bias to the resource where we are relatively best
    # (still using same scoring but computed for the best_t target already).

    cands = []
    # Deterministic tie order: prioritize diagonal/straight toward target, else stay
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Evaluate by how the move changes nearest resource advantage
            self_best = 10**9
            opp_best = 10**9
            for rx, ry in resources:
                self_best = min(self_best, man(nx, ny, rx, ry))
                opp_best = min(opp_best, man(ox, oy, rx, ry))
            # Prefer reducing our distance to the chosen target; also prefer moves where we maintain advantage
            to_target = man(nx, ny, tx, ty)
            to_target_now = man(sx, sy, tx, ty)
            adv = (opp_best - self_best)
            # Slightly discourage stepping adjacent to opponent when not improving
            adjacent_pen = 1 if man(nx, ny, ox, oy) == 1 else 0
            key = (-adv, to_target, adjacent_pen, dx, dy, 0 if (dx == 0 or dy == 0) else 1, to_target_now - to_target)
            cands.append((key, [dx, dy]))

    # Consider staying still as fallback
    nx, ny = sx, sy
    self_best = 10**9
    opp_best = 10**9
    for rx, ry in resources:
        self_best = min(self_best, man(nx, ny, rx, ry))
        opp_best = min(opp_best, man(ox, oy, rx, ry))
    adv = (opp_best - self_best)
    to_target = man(nx, ny, tx, ty)
    adjacent_pen = 1 if man(nx, ny, ox, oy) == 1 else 0
    best_key = (-adv, to_target, adjacent_pen, 0, 0, 0, 0)
    best_move = [0, 0]
    best = None

    if cands:
        for key, mv in cands:
            if best is None or key < best_key:
                best_key = key
                best_move = mv
                best = mv

    return [int(best_move[0]), int(best_move[1])]