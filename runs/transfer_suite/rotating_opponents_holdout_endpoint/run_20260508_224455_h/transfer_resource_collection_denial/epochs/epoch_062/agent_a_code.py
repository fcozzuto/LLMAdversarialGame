def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                if (x + dx, y + dy) in obstacles: c += 1
        return c

    # Choose target resource: prioritize having a closer (or equal) distance than opponent.
    # If none, pick minimal disadvantage (sd-od), then closest to us, then deterministic tie-break.
    best = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not valid(rx, ry): 
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # higher is better
        # Key: prefer lead>0, then maximize lead, then minimize (sd+near obstacle), then lexicographic
        near_pen = obst_near(rx, ry)
        key = (0 if lead > 0 else 1, -lead, sd + near_pen * 2, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No valid resource: move away from opponent a bit if possible.
        tx, ty = sx - (ox - sx), sy - (oy - sy)
    else:
        tx, ty = best[0], best[1]

    # Greedy step toward (tx,ty) while avoiding obstacles; prefer minimizing opponent's distance too.
    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        dself = cheb(nx, ny, tx, ty)
        dob = cheb(ox, oy, tx, ty)  # opponent target distance fixed for one-step evaluation
        # Prefer closer-to-target for us, and slightly prefer actions that don't let opponent get closer.
        # Also avoid stepping near obstacles.
        step_near = obst_near(nx, ny)
        lead_after = (dob - dself)
        key = (-lead_after, dself + step_near * 2, nx - ox + (ny - oy) * 0, nx, ny, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]