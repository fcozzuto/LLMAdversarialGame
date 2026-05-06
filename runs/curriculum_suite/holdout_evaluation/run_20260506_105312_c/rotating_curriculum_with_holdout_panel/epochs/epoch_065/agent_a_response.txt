def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (d, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_cells.append((int(r[0]), int(r[1])))
    if not res_cells:
        return [0, 0]

    # Choose move that maximizes advantage to the best reachable target after this step.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        step_best = None
        for tx, ty in res_cells:
            d_self = man(nx, ny, tx, ty)
            d_opp = man(ox, oy, tx, ty)
            # Strongly prefer targets where we can arrive at least as fast as opponent.
            adv = d_opp - d_self
            # Small tie-break: prefer closer targets for execution reliability.
            key = (-adv, d_self, tx, ty)
            if step_best is None or key < step_best[0]:
                step_best = (key, adv)
        if step_best is None:
            continue
        # Add a mild preference to keep moving towards the "currently best" cell set.
        overall_key = (step_best[0][0], step_best[0][1], dx, dy)
        if best_move is None or overall_key < best_move[0]:
            best_move = (overall_key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]