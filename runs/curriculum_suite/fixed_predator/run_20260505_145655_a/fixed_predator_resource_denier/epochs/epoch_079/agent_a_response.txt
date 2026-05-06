def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def step_towards(px, py, tx, ty):
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if not legal(nx, ny):
                    continue
                d = man(nx, ny, tx, ty)
                key = (d, abs(dx) + abs(dy), dx, dy)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
        if best is None:
            return 0, 0
        return best[1], best[2]

    # Predict opponent's next target: closest resource to them (deterministic tie by coords).
    def pick_opp_target():
        best = None
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        return best[1], best[2]

    tx, ty = pick_opp_target()

    our_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                our_moves.append((dx, dy, nx, ny))
    if not our_moves:
        return [0, 0]

    opp_dx, opp_dy = step_towards(ox, oy, tx, ty)
    opp_nx, opp_ny = ox + opp_dx, oy + opp_dy

    best_move = None
    for dx, dy, nx, ny in our_moves:
        d_us = man(nx, ny, tx, ty)
        d_opp = man(opp_nx, opp_ny, tx, ty)
        on_res = 1 if (nx, ny) in resources else 0
        # Prefer immediate pickup; otherwise maximize distance advantage over opponent.
        val = on_res * 1000 + (d_opp - d_us) * 10 - man(nx, ny, tx, ty)
        # Small preference to reduce drift deterministically
        val -= (abs(nx - sx) + abs(ny - sy)) * 0.01
        key = (-val, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]