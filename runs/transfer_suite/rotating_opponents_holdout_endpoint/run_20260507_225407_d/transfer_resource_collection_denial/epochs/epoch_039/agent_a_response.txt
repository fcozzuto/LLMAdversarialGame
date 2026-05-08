def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer a resource where we are closer than the opponent; otherwise, pick most contested (largest advantage).
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        x, y = r[0], r[1]
        if not inb(x, y) or (x, y) in obs:
            continue
        ds = manh(sx, sy, x, y)
        do = manh(ox, oy, x, y)
        advantage = do - ds  # positive => we are ahead
        # Key: maximize advantage; then smaller our distance; then deterministic tie by position
        key = (-advantage, ds, (x + y), x, y)
        if best_key is None or key < best_key:
            best_key, best = key, (x, y)

    if best is None:
        # No valid resources: step toward opponent's corner to encourage disruption (deterministic)
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the next cell is an obstacle, try deterministic alternatives (stay, or reduce one component).
    nx, ny = sx + dx, sy + dy
    if (inb(nx, ny) and (nx, ny) not in obs) or not inb(nx, ny):
        return [dx, dy]

    # Deterministic fallback order
    candidates = [(0, 0), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (dx, dy)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [cdx, cdy]
    return [0, 0]