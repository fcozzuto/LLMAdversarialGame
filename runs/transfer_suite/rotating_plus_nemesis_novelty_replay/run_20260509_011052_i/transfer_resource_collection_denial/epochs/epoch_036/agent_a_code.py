def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**9
    for x, y in resources:
        ds = dist(sx, sy, x, y)
        do = dist(ox, oy, x, y)
        # Prefer resources we can reach sooner; otherwise reduce opponent advantage.
        val = (do - ds) * 10 - ds
        if ds <= do:
            val += 1000
        # Tie-break deterministically by coordinates.
        if val > best_val or (val == best_val and (x, y) < best):
            best_val = val
            best = (x, y)

    tx, ty = best
    step_opts = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                step_opts.append((dx, dy))
    if not step_opts:
        return [0, 0]

    # Move to step that minimizes our Chebyshev distance to target; deterministic tie-break.
    best_step = None
    best_sd = 10**9
    for dx, dy in step_opts:
        nx, ny = sx + dx, sy + dy
        sd = dist(nx, ny, tx, ty)
        if sd < best_sd or (sd == best_sd and (dx, dy) < best_step):
            best_sd = sd
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]