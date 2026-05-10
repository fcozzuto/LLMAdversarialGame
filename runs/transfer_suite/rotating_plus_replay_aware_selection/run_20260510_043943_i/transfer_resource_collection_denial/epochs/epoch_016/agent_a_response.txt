def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_moves = set()
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            opp_moves.add((nx, ny))

    if not resources:
        # Evade: maximize distance from opponent while not colliding with obstacles
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
            if best_score is None or sc > best_score:
                best_score = sc
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Target resources the opponent is less likely to contest: large (opp_d - self_d),
    # with tie-breaking for smaller self distance.
    tx, ty = None, None
    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        key = (od - sd, -sd, rx, ry)  # maximize advantage against denier
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry
            best = (rx, ry)

    # Choose one move among valid neighbors to (1) reduce distance to target,
    # (2) increase distance from opponent (and avoid stepping into their reachable set).
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_moves:
            penalty = 10
        else:
            penalty = 0
        sc = (-(man(nx, ny, tx, ty)) - penalty, man(nx, ny, ox, oy), -man(nx, ny, sx, sy))
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]