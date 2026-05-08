def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evader" in self_role) and ("pursuer" not in self_role)
    self_is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)
    if not (self_is_evader or self_is_pursuer):
        self_is_evader = ("evader" in opponent_role) and ("pursuer" not in opponent_role)
    is_evader = self_is_evader and not self_is_pursuer

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Prefer evasion from immediate pursuit; pursuer advances while dodging obstacles.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    goal_corner = corners[phase]

    best = (None, -10**18) if is_evader else (None, 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev for diagonal speed
        # obstacle proximity penalty (more is worse)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in blocked:
                    prox += 1

        # wall bias: keep toward safer boundary line depending on role
        wall_bonus = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        wall_bias = -wall_bonus  # closer to wall tends to constrain pursuer

        # evader also prefers to drift toward a corner that is far from pursuer
        corner_dist = abs(nx - goal_corner[0]) + abs(ny - goal_corner[1])
        if is_evader:
            score = (dist * 10) - (prox * 3) + (wall_bias * 0.5) - (corner_dist * 0.02)
            if score > best[1]:
                best = ([dx, dy], score)
        else:
            score = (dist * 10) + (prox * 3) - (wall_bias * 0.5) + (corner_dist * 0.02)
            if score < best[1]:
                best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]