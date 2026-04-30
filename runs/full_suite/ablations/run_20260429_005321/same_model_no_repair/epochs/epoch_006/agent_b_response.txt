def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w // 2, h // 2)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Decide mode: contest a resource where we are not farther than opponent; otherwise chase opponent to disrupt.
    best_res = None
    best_key = None
    any_we_not_farther = False
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd <= od:
            any_we_not_farther = True
            key = (od - sd, -sd, -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)

    mode = "contest" if any_we_not_farther else "chase"
    if mode == "chase":
        # Target the resource where opponent is most advantaged, just to bias movement (blocking).
        worst_res = None
        worst_key = None
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (-(sd - od), -od, -(rx + ry))  # most negative (sd-od) => biggest opponent advantage
            if worst_key is None or key > worst_key:
                worst_key = key
                worst_res = (rx, ry)
        block_res = worst_res

    # Evaluate moves deterministically with parity-based tie break.
    parity = observation.get("turn_index", 0)