def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    best_t = resources[0]
    best_s = -10**18
    for tx, ty in resources:
        dus = dist(sx, sy, tx, ty)
        dop = dist(ox, oy, tx, ty)
        # Prefer resources we can reach first; slightly bias toward closer overall.
        if dus < dop:
            s = 10000 - dus * 50 + (dop - dus) * 200
        elif dus == dop:
            s = 2000 - dus * 50 - (tx + ty) * 0.01
        else:
            s = -10000 - dus * 50 - (dus - dop) * 250
        if s > best_s or (s == best_s and (tx, ty) < best_t):
            best_s = s
            best_t = (tx, ty)
    tx, ty = best_t
    if (sx, sy) == (tx, ty):
        return [0, 0]
    # Step toward target, but only among valid moves; use deterministic tie-break.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d = dist(nx, ny, tx, ty)
            # secondary: prefer reducing opponent advantage if possible
            dop = dist(ox, oy, tx, ty)
            candidates.append((d, -dop, dx, dy))
    candidates.sort()
    return [candidates[0][2], candidates[0][3]]