def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    r = (ti % 9 + 9) % 9
    moves = moves[r:] + moves[:r]

    def dist(a, b):
        ax, ay = a; bx, by = b
        return (ax - bx) * (ax - bx) + (ay - by) * (ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = ox, oy
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist((nx, ny), (tx, ty))
            score = d + 0.001 * (abs(nx - sx) + abs(ny - sy))
            if score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_score = 10**18
    best_move = (0, 0)
    opp_factor = 0.25

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best target from this next position, preferring targets I can beat the opponent to.
        best_for_move = 10**18
        for rx, ry in resources:
            d_me = dist((nx, ny), (rx, ry))
            d_op = dist((ox, oy), (rx, ry))
            # Lower is better: prioritize reaching quickly; discourage targets where opponent is much closer.
            score = d_me - opp_factor * d_op
            # Small deterministic tie-break to reduce jitter near equals.
            score += 0.0001 * (abs(nx - rx) + abs(ny - ry))
            if score < best_for_move:
                best_for_move = score

        if best_for_move < best_score:
            best_score = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]