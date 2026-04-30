def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If we're somehow on invalid tile, try to step off deterministically.
    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource where we have the best (closest-than-opponent) advantage.
    target = None
    if resources:
        best_key = None
        for rx, ry in resources:
            d_us = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            key = (d_us - d_op, d_us, rx, ry)  # smallest first
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is None:
            # No resources visible: maximize distance from opponent and avoid obstacles.
            score = cheb(nx, ny, ox, oy)
        else:
            rx, ry = target
            d_new = cheb(nx, ny, rx, ry)
            d_op_target = cheb(ox, oy, rx, ry)

            # Strongly prefer decreasing our distance to target and increasing opponent's effective pressure.
            d_op_if_we_approach = d_op_target  # opponent position fixed this turn
            # Also include separation to avoid being too close.
            sep = cheb(nx, ny, ox, oy)

            # Score: higher is better
            score = (
                -d_new * 100
                + d_op_if_we_approach * 2
                + sep * 3
            )

            # Small deterministic tiebreak: prefer moving toward target (lower d to target from tie perspective).
            score += - (dx * 0.01 + dy * 0.001)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            # Deterministic tie-break: lexicographically smaller move.
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]