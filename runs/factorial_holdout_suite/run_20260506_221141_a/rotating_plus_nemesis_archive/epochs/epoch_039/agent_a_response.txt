def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not (isinstance(sx, int) and isinstance(sy, int) and inb(sx, sy)):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and inb(ox, oy)):
        ox, oy = w - 1, h - 1

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                obs.add((x, y))

    best = None
    best_val = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        x, y = r[0], r[1]
        if not (isinstance(x, int) and isinstance(y, int) and inb(x, y)):
            continue
        if (x, y) in obs:
            continue
        ds = max(abs(sx - x), abs(sy - y))
        do = max(abs(ox - x), abs(oy - y))
        # Prefer resources we can reach first; also prefer closer overall.
        val = (do - ds) * 1000 - ds
        if val > best_val:
            best_val = val
            best = (x, y)

    if best is None:
        # Fallback: move away from opponent if nothing visible
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        if (sx + dx, sy + dy) in obs:
            if (sx + dx, sy) not in obs:
                dy = 0
            elif (sx, sy + dy) not in obs:
                dx = 0
            else:
                dx = 0
                dy = 0
        return [dx, dy]

    tx, ty = best
    # Step toward target (diagonal allowed)
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If diagonal step is blocked, try axis moves deterministically.
    cand = [(step_dx, step_dy), (step_dx, 0), (0, step_dy), (0, 0)]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]