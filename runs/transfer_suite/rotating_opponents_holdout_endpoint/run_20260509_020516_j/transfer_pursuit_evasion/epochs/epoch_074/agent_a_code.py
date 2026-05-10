def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) and ("evader" not in opp_role)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Favor staying/advancing along a direct line to opponent, but dodge walls via local clearance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        # Local clearance: count free neighbors (incl. diagonals) to avoid getting trapped.
        free = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inside(tx, ty):
                    free += 1

        # Edge preference: keep away from corners as evader, but allow if needed.
        edge_dist = min(nx, ny, w - 1 - nx, h - 1 - ny)

        # Small deterministic tie-break: prefer moves with smaller dx,dy index ordering already in moves.
        if evader:
            val = (-d2) + (-free * 0.35) + (-(edge_dist) * 0.05)
        else:
            val = (d2) + (-free * 0.25) + (-(edge_dist) * 0.02)

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]