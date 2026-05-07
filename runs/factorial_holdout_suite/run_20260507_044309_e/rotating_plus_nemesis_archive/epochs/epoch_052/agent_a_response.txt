def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick best target by "race": prioritize targets where we can reach no later than opponent, else closest race deficit.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        race = do - ds  # positive means we are earlier or equal
        key = (race < 0, -race, ds, rx, ry)
        if best_target is None or key < best_key:
            best_target, best_key = (rx, ry), key

    tx, ty = best_target

    # Local obstacle-aware move selection: evaluate all deltas that stay in bounds and not on obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                ds = cheb(nx, ny, tx, ty)
                # Compare relative progress vs opponent (opponent position treated as static for this one-step lookahead).
                do = cheb(ox, oy, tx, ty)
                race = do - ds
                # Prefer making us earlier (race), then reducing our distance.
                key = (race < 0, -race, ds, abs(nx - tx) + abs(ny - ty), nx, ny)
                candidates.append((key, dx, dy))
    candidates.sort(key=lambda t: t[0])
    return [int(candidates[0][1]), int(candidates[0][2])]