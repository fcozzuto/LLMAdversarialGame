def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]
    tr = observation.get("turns_remaining", 0)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target_for(px, py):
        best = None
        best_key = None
        for rx, ry in resources:
            d_self = man(px, py, rx, ry)
            key = (d_self, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    opp_tx, opp_ty = best_target_for(ox, oy)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def move_value(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            return -10**9
        # If we would step onto opponent, still allowed by engine; just treat as blocked.
        if (nx, ny) == (ox, oy):
            return -10**8
        # Prefer immediate collection by stepping onto a resource.
        if (nx, ny) in obstacles:
            return -10**9
        if any(rx == nx and ry == ny for rx, ry in resources):
            return 10**6
        # Otherwise, choose target that maximizes advantage.
        # Near end, just go greedy nearest; earlier, avoid giving up a resource too easily.
        if tr <= 4:
            tgt = min(resources, key=lambda p: (man(nx, ny, p[0], p[1]), p[0], p[1]))
            return 1000 - man(nx, ny, tgt[0], tgt[1])
        best = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # If opponent targets a cell, bias to contest it when possible; otherwise avoid losing it.
            contest = 1 if (rx, ry) == (opp_tx, opp_ty) else 0
            adv = (do - ds) + 0.35 * contest
            # Mild preference to reduce distance to the opponent's target path line (deterministic, cheap).
            line_bias = 0
            if opp_tx == rx:
                line_bias = 0.1 * (abs(ny - ry) == 0)
            if opp_ty == ry:
                line_bias = 0.1 * (abs(nx - rx) == 0)
            cand = adv * 10 + (100 - ds) + line_bias
            if cand > best:
                best = cand
        return best

    best_move = (0, 0)
    best_val = -10**12
    for dx, dy in moves:
        v = move_value(dx, dy)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]