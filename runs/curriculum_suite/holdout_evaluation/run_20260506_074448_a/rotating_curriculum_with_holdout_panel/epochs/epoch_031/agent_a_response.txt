def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    k = 0.65
    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_to_opp = man(nx, ny, ox, oy)
        total = 0.0
        # Prefer moves that create strong relative advantage on some resource,
        # while not allowing moves that hand resources to the opponent.
        best_adv = None
        worst_hand = 0.0

        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Higher is better: advantage ~ (opd - myd), with normalization by my distance.
            adv = (opd - myd) - 0.15 * myd
            if best_adv is None or adv > best_adv:
                best_adv = adv
            # Penalty if opponent can get there significantly earlier.
            if opd + 0.5 < myd:
                worst_hand += (myd - opd)

        # Tie-break deterministically: slight preference to stay farther from opponent
        # unless it strongly harms resource race.
        val = (best_adv if best_adv is not None else -1e9) - 0.03 * my_to_opp - 0.06 * worst_hand
        if best_val is None or val > best_val + 1e-12:
            best_val = val
            best_move = [dx, dy]
        elif best_val is not None and abs(val - best_val) <= 1e-12:
            # Deterministic tie-break: prefer closer to the single best resource target.
            if best_val is None:
                best_move = [dx, dy]
            else:
                # compare my distance to best resource from current move
                # (compute quickly by reusing best_adv resource choice implicitly)
                # just use my_to_opp and my distance to closest resource
                my_closest = min(manh(nx, ny, rx, ry) for rx, ry in resources)
                cur_closest = min(manh(sx + best_move[0], sy + best_move[1], rx, ry) for rx, ry in resources)
                if my_closest < cur_closest or (my_closest == cur_closest and my_to_opp < man(sx + best_move[0], sy + best_move[1], ox, oy)):
                    best_move = [dx, dy]

    return best_move