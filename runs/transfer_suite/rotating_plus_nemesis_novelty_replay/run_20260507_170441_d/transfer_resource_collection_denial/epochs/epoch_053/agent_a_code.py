def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def clamp_step(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return dx, dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Score targets: maximize our lead; break ties by smaller our distance; then deterministic by coords.
    best_t = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        adv = op_d - my_d  # positive => we arrive sooner
        sweep_bias = 0
        if oy == ry:  # opponent likely sweeping along rows
            sweep_bias = -0.25  # slightly penalize same-row late targets
        if ox == rx:
            sweep_bias = sweep_bias - 0.10
        key = (-adv, my_d, rx, ry, sweep_bias)
        if best_t is None or key < best_t[0]:
            best_t = (key, rx, ry)
    _, tx, ty = best_t

    # Greedy move reducing king distance to target; if blocked, choose best among valid neighbors by target lead.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    def objective(nx, ny):
        my_d = dist8(nx, ny, tx, ty)
        op_d = dist8(ox, oy, tx, ty)
        return (-(op_d - my_d), my_d, nx, ny)

    # Try direct step(s) first
    primary = [(dx0, dy0), (dx0, 0), (0, dy0)]
    for ddx, ddy in primary:
        ddx, ddy = clamp_step(ddx, ddy)
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny):
            return [ddx, ddy]

    # Fallback: best valid neighbor by objective
    best_m = None
    for ddx, ddy in moves:
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny):
            continue
        obj = objective(nx, ny)
        if best_m is None or obj < best_m[0]:
            best_m = (obj, ddx, ddy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[1]), int(best_m[2])]