def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    env = (observation.get("environment_name", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("evad" in env) or ("escape" in env) or ("evasion" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            if inb(x + dx, y + dy):
                c += 1
        return c

    best_move = (0, 0)
    best_key = None

    cur_mob = mobility(sx, sy)

    # deterministic preference: based on move order already, tie-break by lexicographic (dx,dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)

        # obstacle proximity penalty to avoid "sticking" near blocks
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    prox += 1

        mob = mobility(nx, ny)
        # primary objective: approach (pursuer) or flee (evader)
        if is_evader:
            # maximize distance, then maximize mobility, then minimize obstacle proximity
            key = (dist, mob, -prox)
        else:
            # minimize distance, then maximize mobility, then minimize obstacle proximity
            key = (-dist, mob, -prox)

        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
        elif key == best_key:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    # If current position is better trapped, still return something valid (should be).
    if not inb(sx + best_move[0], sy + best_move[1]):
        # fall back to any valid move deterministically
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]