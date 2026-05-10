def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    rlist = [tuple(r) for r in resources]
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick a target resource that maximizes our "reach advantage".
    best_t = None
    best_key = None
    for rx, ry in rlist:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        # Higher advantage is better; also prefer closer/easier cells.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Score candidate moves from the immediate next position.
    tset = set(rlist)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: immediate pickup, then advantage vs target, then improvement toward other good resources.
        immediate = 1 if (nx, ny) in tset else 0
        sd_t = abs(tx - nx) + abs(ty - ny)
        od_t = abs(tx - ox) + abs(ty - oy)
        adv = od_t - sd_t  # higher means we stay ahead of opponent on target

        # Secondary: consider best advantage among all resources (cheap heuristic, small list).
        best_other_adv = -10**9
        for rx, ry in rlist:
            sd = abs(rx - nx) + abs(ry - ny)
            od = abs(rx - ox) + abs(ry - oy)
            a = od - sd
            if a > best_other_adv:
                best_other_adv = a

        # Deterministic tie-breaking by lexicographic move order.
        score = (immediate, best_other_adv, adv, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]