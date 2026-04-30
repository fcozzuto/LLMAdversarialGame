def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target that we are more likely to grab (arrive earlier or not too much later).
    target = None
    best_gain = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds  # higher is better for us
        if best_gain is None or gain > best_gain or (gain == best_gain and ds < cheb(sx, sy, target[0], target[1])):
            best_gain = gain
            target = (rx, ry)

    if target is None:
        return [0, 0]

    tx, ty = target

    # Evaluate our immediate move with an "win more / don't lose" heuristic.
    # Primary: reduce our distance to target; Secondary: increase opponent distance to that target.
    # Tertiary: avoid stepping into tight obstacle neighbors.
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def risk(x, y):
        r = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                r += 1
        return r

    best = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ds_next = cheb(nx, ny, tx, ty)
        do_curr = cheb(ox, oy, tx, ty)
        do_if_adj = cheb(ox, oy, tx, ty)  # opponent move unknown; keep stable
        # Prefer moves that improve our relative position to the target.
        rel = do_curr - ds_next
        score = (rel * 10) - ds_next - (risk(nx, ny) * 0.5) + (0.2 if (tx, ty) == (nx, ny) else 0)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]