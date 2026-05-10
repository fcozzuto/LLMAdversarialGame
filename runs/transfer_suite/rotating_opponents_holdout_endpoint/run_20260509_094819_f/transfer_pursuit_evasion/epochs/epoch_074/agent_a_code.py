def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    pursuer = (observation.get("self_role", "pursuer") != "evader")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_corner_dist(tx, ty, agentx, agenty):
        # Use Chebyshev to match diagonal capture dynamics
        return max(max(abs(tx - ax), abs(ty - ay)) for ax, ay in [(agentx, agenty)])

    # Pick a strategic corner to bias against wall-running evasion
    if pursuer:
        # Move toward the corner that is farthest from the evader (so we can cut off), but via chase anyway
        target_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        # Flee toward farthest corner from pursuer
        target_corner = max(corners, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy) + 2 * max(abs(c[0] - ox), abs(c[1] - oy)))

    tx, ty = target_corner

    def score(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))
        # Gentle bias toward corner to handle wall-run; also prefer not to "waste" distance
        corner_d = max(abs(nx - tx), abs(ny - ty))
        # If pursuer, minimize opponent distance and reduce corner distance to cut off.
        # If evader, maximize opponent distance and increase corner distance to cling to wall-corner.
        if pursuer:
            return (-d, -corner_d, 0)
        else:
            return (d, corner_d, 0)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score(nx, ny)
        # Deterministic tie-breaker on move ordering
        if best is None or sc > best or (sc == best and (dx, dy) < tuple(best_move)):
            best = sc
            best_move = [dx, dy]

    return best_move