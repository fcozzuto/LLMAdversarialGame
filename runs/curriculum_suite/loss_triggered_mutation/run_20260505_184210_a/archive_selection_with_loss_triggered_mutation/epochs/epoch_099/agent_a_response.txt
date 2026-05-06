def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # fallback: move away from opponent if possible, else stay
        best = (1e9, 1e9, 0, 0)
        chosen = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man((nx, ny), (ox, oy))
            if ( -d, man((nx, ny), (w - 1, h - 1)), dx, dy) < best:
                best = (-d, man((nx, ny), (w - 1, h - 1)), dx, dy)
                chosen = (dx, dy)
        return [chosen[0], chosen[1]]

    # Target selection: maximize advantage over opponent (self faster), with tie by closer to self.
    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = man((sx, sy), (tx, ty))
        od = man((ox, oy), (tx, ty))
        # Key: higher advantage first, then smaller self distance, then position bias deterministic
        adv = od - sd
        key = (-adv, sd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    sd0 = man((sx, sy), (tx, ty))
    chosen = (0, 0)
    best_move_key = None

    # Move selection: reduce distance to target, avoid obstacles, and slightly increase distance to opponent.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = man((nx, ny), (tx, ty))
        od = man((nx, ny), (ox, oy))
        # Prefer progress; discourage giving opponent too much closeness (small weight), deterministic tie-breakers.
        move_key = (sd, -od, dx, dy)
        if best_move_key is None or move_key < best_move_key:
            best_move_key = move_key
            chosen = (dx, dy)

    # If all moves blocked, stay.
    if best_move_key is None:
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]