def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer winning resources, and for equal win margin prefer quicker and safer paths.
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int)):
            continue
        if not in_bounds(tx, ty):
            continue
        if (tx, ty) in blocked:
            continue
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        # "win" positive means we reach earlier/equal; also bias against long detours via obstacles by locally checking next-step viability.
        if myd == 0:
            key = (1, 0, tx + ty * 0.0001)
        else:
            key = (1 if myd <= opd else 0, (opd - myd) if myd <= opd else -(myd - opd), -myd, tx + ty * 0.0001)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty, myd, opd)

    # Candidate moves: 8 directions + stay; pick move that maximizes improvement in winning target.
    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if best is None:
        # If no target, move toward center-ish while avoiding obstacles (deterministic).
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_m, best_d = [0, 0], None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in blocked:
                continue
            d = manh(nx, ny, cx, cy)
            if best_d is None or d < best_d:
                best_d = d
                best_m = [dx, dy]
        return best_m

    tx, ty, myd, opd = best

    def step_ok(x, y):
        return in_bounds(x, y) and (x, y) not in blocked

    # Scoring: choose move that reduces distance to target; if target is not winnable now, still reduce (to contest).
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        nm = manh(nx, ny, tx, ty)
        no = manh(ox, oy, tx, ty)
        # Encourage staying on course (smaller nm), and if we can win, maximize margin after move.
        win_margin = (no - nm)
        score = (1 if nm <= no else 0, win_margin, -nm, -abs((nx - ox)) - abs((ny - oy)), dx * 0.0001 + dy * 0.00001)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move