def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    tied = 0

    # If resources exist, greedily target the closest; otherwise just drift away from opponent.
    target_hint = None
    if resources:
        target_hint = min(resources, key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            d_self_min = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            # Also consider how close opponent would be to that same "frontier"
            # by taking average closeness to the nearest few resources.
            d_opp_min = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            # Deterministic tie-break toward lower coords.
            score = -10 * d_self_min + 3 * d_opp_min
            if target_hint is not None:
                score += 2 * (-cheb(nx, ny, target_hint[0], target_hint[1]))
            # Small preference to reduce distance to opponent when it would matter (endgame pressure).
            score += -1 * cheb(nx, ny, ox, oy)
            score += -0.01 * (nx + ny)
        else:
            # No resources: move to maximize distance from opponent.
            score = cheb(nx, ny, ox, oy) - 0.01 * (nx + ny)

        if score > best_val:
            best_val = score
            best_move = (dx, dy)
            tied = 0
        elif score == best_val:
            # Deterministic tie-break: prefer moves in a fixed order, then smaller dx,dy.
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]