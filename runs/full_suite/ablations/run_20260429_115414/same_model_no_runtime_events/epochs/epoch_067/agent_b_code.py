def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target we can reach earlier than the opponent; otherwise pick the most contested.
    target = None
    best = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        our_side = -cheb(rx, ry, 0, 0)  # prefer resources nearer our corner (agent_b starts at bottom-right in typical setups, but we don't assume)
        center_bias = -cheb(rx, ry, cx, cy)
        # advantage first; then slight preference for closer-to-us (relative); then center.
        score = (do - ds) * 10 + (ds * -0.1) + our_side * 0.05 + center_bias * 0.02
        # Deterministic tie-break: lexicographically smaller resource.
        if score > best or (score == best and (rx, ry) < target):
            best = score
            target = (rx, ry)

    # If no resources, drift toward center while avoiding opponent.
    if not target:
        tx, ty = cx, cy
    else:
        tx, ty = target

    # Evaluate local moves with opponent-aware objective.
    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_self_to_t = cheb(nx, ny, tx, ty)
        d_opp_to_t = cheb(ox, oy, tx, ty)

        # If we are not clearly ahead on the chosen target, prioritize stealing proximity (reduce opponent access).
        ahead = (d_opp_to_t - d_self_to_t)
        # Also measure how the move changes our distance to opponent (avoid collisions when tied).
        d_self_to_opp = cheb(nx, ny, ox, oy)

        move_center = -cheb(nx, ny, cx, cy)
        # Deterministic tie-break via lexicographic favor on move.
        sc = ahead * 12 - d_self_to_t * 0.3 + move_center * 0.05 + d_self_to_opp * (-0.01)

        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]