def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b): return abs(a[0] - b[0]) if False else 0  # no-op to avoid name clashes
    def dist_cheb(a, b): 
        dx = abs(a[0] - b[0]); dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Choose best target resource by "arrive earlier than opponent"
    best_t = None
    best_v = -10**18
    for r in resources:
        if not valid(r[0], r[1]): 
            continue
        dS = dist_cheb((sx, sy), r)
        dO = dist_cheb((ox, oy), r)
        v = (dO - dS) * 10 - dS  # prioritize winning races, then closeness
        # small deterministic tie-breaker toward top-left
        v -= (r[0] * 0.01 + r[1] * 0.001)
        if v > best_v:
            best_v = v
            best_t = r

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) == (tx, ty):
        # move away from immediate contest to avoid trapping into obstacles
        best_m = [0, 0]; best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            s = dist_cheb((nx, ny), (sx, sy)) - dist_cheb((nx, ny), best_t)
            if s > best_s:
                best_s = s; best_m = [dx, dy]
        return best_m

    # Greedy: among valid moves, maximize improvement vs target and delay opponent
    best_m = [0, 0]; best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS2 = dist_cheb((nx, ny), (tx, ty))
        dO2 = dist_cheb((ox, oy), (tx, ty))
        # Prefer moves that reduce our distance; if race, prefer maximizing margin.
        s = (dO2 - dS2) * 20 - dS2 * 2
        # Deterministic tie-break: prefer moves that head generally toward target
        s -= (abs(nx - tx) + abs(ny - ty)) * 0.001
        if s > best_s:
            best_s = s; best_m = [dx, dy]
    return best_m