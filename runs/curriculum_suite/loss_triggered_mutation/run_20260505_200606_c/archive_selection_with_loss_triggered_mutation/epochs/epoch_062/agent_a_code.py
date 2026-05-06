def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose target resource with deterministic "advantage" scoring
    if resources:
        best = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we are closer; if we are not, still prefer far-from-opponent ones
            score = 2.0 * (od - sd) + 0.05 * od - 0.01 * sd
            key = (score, -od, -sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        _, (tx, ty) = best
    else:
        # No visible resources: move to increase distance from opponent while drifting toward center-ish
        tx, ty = (w // 2, h // 2)

    cur_ds = man(sx, sy, tx, ty)
    cur_do = man(sx, sy, ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = man(nx, ny, tx, ty)
        ndo = man(nx, ny, ox, oy)

        # Heuristic:
        # - Strongly prefer moves that reduce distance to target
        # - Strongly prefer increasing distance from opponent
        # - Mildly avoid moves that are equally good for target but worsen opponent distance
        val = 0.0
        val += (cur_ds - nds) * 10.0
        val += (ndo - cur_do) * 6.0

        # If we are currently far behind at target, prioritize getting safer from opponent
        if resources:
            sdist = cur_ds
            odist = man(ox, oy, tx, ty)
            if odist <= sdist:
                val += (ndo - cur_do) * 4.0

        # Deterministic tie-breaker: prefer diagonals that move toward lower x then lower y (consistent)
        tie = (-dx, -dy, nx - sx, ny - sy)
        val2 = (val, tie)

        if val2 > (best_val, (-best_move[0], -best_move[1], 0, 0)):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]