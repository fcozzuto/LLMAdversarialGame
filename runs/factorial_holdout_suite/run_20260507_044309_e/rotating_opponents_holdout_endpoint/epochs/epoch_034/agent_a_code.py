def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    resources = []
    for p in resources_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def score_target(px, py, tx, ty):
        sd = man(px, py, tx, ty)
        od = man(ox, oy, tx, ty)
        adv = od - sd  # positive => we are closer
        # Prefer taking winning resources, then closest among them, then tie-break by coordinates
        return (adv, -sd, -tx, -ty)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    # Pick best global target from current state
    best_t = resources[0]
    best_k = None
    for tx, ty in resources:
        k = score_target(sx, sy, tx, ty)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (tx, ty)

    tx, ty = best_t

    # One-step lookahead with obstacle-aware candidate moves
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate: prioritize moving toward the chosen target, but allow switching if a better "race" exists
        val = (0, 0, 0, 0)
        # Check if any other resource becomes clearly better after this step
        local_best_k = None
        local_best_t = None
        for rtx, rty in resources:
            k = score_target(nx, ny, rtx, rty)
            if local_best_k is None or k > local_best_k:
                local_best_k = k
                local_best_t = (rtx, rty)
        # Bias toward the chosen target to avoid thrashing
        chosen_bias = 1 if local_best_t == best_t else 0
        sdist = man(nx, ny, tx, ty)
        tdist = man(ox, oy, tx, ty)
        race = tdist - sdist
        val = (chosen_bias, race, -local_best_k[1], -local_best_t[0], -local_best_t[1])
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move