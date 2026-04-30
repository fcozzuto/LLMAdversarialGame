def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    def cheb(a, b, c, d):
        da = a - c
        db = b - d
        if da < 0: da = -da
        if db < 0: db = -db
        return da if da > db else db

    # Target a resource where we are relatively closer than opponent.
    best_r = None
    best_sc = None
    best_sd = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        sc = od - sd
        if best_sc is None or sc > best_sc or (sc == best_sc and (sd < best_sd or (sd == best_sd and (rx, ry) < tuple(best_r)))):
            best_sc = sc
            best_sd = sd
            best_r = (rx, ry)

    tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce distance to target; if tied, move away from opponent; then deterministic.
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx = sx
    cy = sy
    best_delta = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = cx + dx, cy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dcur = cheb(sx, sy, tx, ty)
        dnew = cheb(nx, ny, tx, ty)
        prog = dcur - dnew
        oppd_new = cheb(nx, ny, ox, oy)
        # key: maximize progress, then maximize distance from opponent, then lex.
        key = (prog, oppd_new, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_delta = (dx, dy)

    # If all adjacent moves are blocked, fall back to safe stay or simple deterministic step.
    if best_key is None:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [int(best_delta[0]), int(best_delta[1])]