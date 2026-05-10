def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_target = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        adv = opd - myd
        center_bias = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv, -myd, center_bias, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)
    tx, ty = best_target

    best_move = [0, 0]
    best_score = None

    # One-step lookahead scoring (deterministic).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd1 = cd(nx, ny, tx, ty)

        # Discourage moving into/near opponent while still allowing interception if ahead.
        opd1 = cd(ox, oy, nx, ny)
        opp_pressure = 0
        if opd1 <= 1:
            opp_pressure = 6
        elif opd1 <= 2:
            opp_pressure = 2.5

        # Encourage resource capture now.
        cap = 0
        if (nx, ny) in set(map(tuple, resources)):
            cap = 20

        # Slightly prefer reducing distance to opponent's position when we are ahead (block).
        my_to_opp = cd(nx, ny, ox, oy)
        block = 0
        if cd(sx, sy, tx, ty) < cd(ox, oy, tx, ty):
            block = -0.15 * my_to_opp

        score = (cap + 2.2 * (cd(sx, sy, tx, ty) - myd1) - 1.0 * myd1 - opp_pressure + block)
        # Deterministic tie-break: prefer moves with lexicographically smallest (dx,dy) among equal scores.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    # If all moves were blocked (unlikely), stay.
    return [int(best_move[0]), int(best_move[1])]