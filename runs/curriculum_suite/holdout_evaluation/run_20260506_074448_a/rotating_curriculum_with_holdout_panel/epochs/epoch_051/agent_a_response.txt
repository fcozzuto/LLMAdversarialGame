def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Interception heuristic: pick move that maximizes our advantage to some resource.
        center = -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.002
        move_score = center

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)

            adv = oppd - myd  # positive means we are closer than opponent to this resource
            # Prefer winning races (large adv), but also avoid being too far.
            race = adv * 10.0 - myd * 0.25
            # If we are behind, penalize more aggressively to avoid drifting into dead races.
            if adv < 0:
                race *= 1.8
            move_score = max(move_score, center + race)

        # Tie-break deterministically: prefer not moving diagonally last, then lexicographic.
        tiebreak = (-(dx == 0 and dy == 0), - (dx != 0 and dy != 0), dx, dy)
        if move_score > best_score or (move_score == best_score and tiebreak > (-(best_move[0] == 0 and best_move[1] == 0), - (best_move[0] != 0 and best_move[1] != 0), best_move[0], best_move[1])):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]