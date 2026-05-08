def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole)
    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in oset

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer diagonals slightly when tie-breaking.
    def dist_score(nx, ny):
        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)
        if is_pursuer:
            return (cheb, man)  # minimize
        else:
            return (-cheb, -man)  # maximize

    best = None
    best_mv = (0, 0)
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not legal(nx, ny):
            continue
        score = dist_score(nx, ny)
        # Tie-break: diagonal preference, then smaller manhattan from/to opponent, then stable prefer (0,0).
        diag = 1 if (dx != 0 and dy != 0) else 0
        man_sep = abs(nx - ox) + abs(ny - oy)
        tup = (score, -diag if is_pursuer else diag, man_sep if is_pursuer else -man_sep, (dx, dy) == (0, 0))
        if best is None or (is_pursuer and tup < best) or ((not is_pursuer) and tup < best):
            best = tup
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]