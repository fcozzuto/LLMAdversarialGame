def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    remaining = observation.get("remaining_resource_count", None)
    rem_bias = 0
    if isinstance(remaining, int):
        rem_bias = (remaining - len(resources)) * 0.0  # keep deterministic, effectively no bias

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        # Choose the resource that maximizes our advantage after this move.
        best_for_move = -10**9
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where opponent is further (or we are much closer).
            val = (od - sd) * 1000 - sd * 3 + rem_bias
            # Small deterministic tiebreak: lexicographic on resource position.
            val += (0.000001 * (rx * 8 + ry))
            if val > best_for_move:
                best_for_move = val
        # Prefer moves that don't give up too much immediate closeness if ties.
        if best_for_move > best[1]:
            best = ((dx, dy), best_for_move)
        elif best_for_move == best[1] and best[0] is not None:
            # deterministic tie-break order by dx, then dy
            if (dx, dy) < best[0]:
                best = ((dx, dy), best_for_move)

    dx, dy = best[0] if best[0] is not None else (0, 0)
    return [int(dx), int(dy)]