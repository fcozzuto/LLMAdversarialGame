def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("evad" not in self_role) if self_role else ("evad" in opponent_role or opponent_role == "")
    if not self_role and opponent_role:
        pursuer = ("evad" not in opponent_role)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target_tx, target_ty = ox, oy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = [0, 0]
    best_score = None

    # For evader: add bias to head toward the safest corner relative to pursuer
    corner = None
    if not pursuer:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # choose corner that maximizes distance from pursuer
        corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        target_tx, target_ty = corner[0], corner[1]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        dist_to_op = abs(nx - ox) + abs(ny - oy)

        # obstacle proximity penalty (simple local check)
        penalty = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs_set:
                    penalty += 2

        if pursuer:
            # move closer to opponent
            val = -dist_to_op
            # encourage also approaching target corner if roles mismatch oddities
            val += -0.05 * (abs(nx - target_tx) + abs(ny - target_ty))
        else:
            # move away from opponent; also bias toward chosen corner
            val = dist_to_op
            val += 0.03 * (abs(nx - target_tx) + abs(ny - target_ty))

        val -= penalty

        # deterministic tie-break: prefer larger val, then smaller dx,dy lexicographically
        tie = (val, -abs(dx), -abs(dy), -nx, -ny)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]