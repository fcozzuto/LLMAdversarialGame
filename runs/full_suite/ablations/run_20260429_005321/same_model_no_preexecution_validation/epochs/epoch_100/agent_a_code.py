def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b, c, d):
        dx = a - c; dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # No resources: drift toward center while staying safe and slightly away from opponent.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0); best = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            dcen = cheb(nx, ny, cx, cy)
            dop = cheb(nx, ny, ox, oy)
            val = (-dcen) + 0.1 * dop
            if val > best:
                best = val; best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Choose best target based on current relative distances (Chebyshev) and deterministic tie-break.
    best_targets = []
    best_rank = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: being closer than opponent, also prefer nearer resources overall.
        rank = (opd - myd) * 1000 - myd
        rank += (rx * 0.01 + ry * 0.001)  # deterministic tie-break
        if rank > best_rank:
            best_rank = rank
            best_targets = [(rx, ry)]
        elif rank == best_rank:
            best_targets.append((rx, ry))
    best_targets.sort()
    target = best_targets[0]

    tx, ty = target

    # Evaluate next move locally: move toward target, avoid corners/obstacles, and contest resource when relevant.
    best_move = (0, 0); best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        my_to_t = cheb(nx, ny, tx, ty)
        my_now = cheb(sx, sy, tx, ty)

        # Stay competitive against opponent for target: prefer states where I'm at least as close as opponent.
        op_to_t = cheb(ox, oy, tx, ty)
        rel_now = my_now - op_to_t
        rel_next = my_to_t - op_to_t

        # Safety: penalize having fewer free neighbors after move (prevents obstacle hits/stuck).
        free_count = 0
        for adx, ady in dirs:
            axp, ayp = nx + adx, ny + ady
            if free(axp, ayp):
                free_count += 1

        # Also lightly favor moving away from opponent to reduce interference unless contesting target.
        dop_now = cheb(sx, sy, ox, oy)
        dop_next = cheb(nx, ny, ox, oy)

        # Deterministic extra tie-break by position
        tie = -(nx * 0.01 + ny * 0.001)

        val = 0
        val += (my_now - my_to_t) * 10.0
        # If I'm behind, reduce gap; if ahead, keep/expand.
        val += (rel_now -