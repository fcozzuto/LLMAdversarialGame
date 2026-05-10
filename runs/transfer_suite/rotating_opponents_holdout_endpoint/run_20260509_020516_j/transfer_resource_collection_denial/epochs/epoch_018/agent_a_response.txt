def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    valid_positions = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid_positions.append((dx, dy, nx, ny))
    if not valid_positions:
        valid_positions = [(0, 0, sx, sy)]

    # Evaluate moves by the best "future advantage" from the resulting position.
    # Advantage: opponent distance to resource minus my distance to resource.
    # Also strongly prefer stepping onto a resource immediately.
    best_move = (0, 0, -10**18)
    for dx, dy, nx, ny in valid_positions:
        if (nx, ny) in obstacles:
            continue
        immediate = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        rset = set(tuple(r) for r in resources)
        if immediate:
            score = 10**12 - (man(nx, ny, ox, oy) * 10)  # deterministic tie-break
        else:
            best_adv = -10**18
            best_tie = (10**9, 10**9)  # (my_dist, rx, ry)
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                md = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                adv = od - md
                if adv > best_adv or (adv == best_adv and (md < best_tie[0] or (md == best_tie[0] and (rx, ry) < (best_tie[1], best_tie[2])))):
                    best_adv = adv
                    best_tie = (md, rx, ry)
            # Encourage reducing my distance to the chosen resource, and slightly discourage giving opponent closer routes.
            myd = best_tie[0]
            # If I'm behind (best_adv negative), still try to maximize adv (intercept), not just chase.
            score = best_adv * 1000 - myd - (man(ox, oy, nx, ny) * 2) + (man(nx, ny, ox, oy) == 0) * 5
        if score > best_move[2] or (score == best_move[2] and (dx, dy) < (best_move[0], best_move[1])):
            best_move = (dx, dy, score)

    return [int(best_move[0]), int(best_move[1])]