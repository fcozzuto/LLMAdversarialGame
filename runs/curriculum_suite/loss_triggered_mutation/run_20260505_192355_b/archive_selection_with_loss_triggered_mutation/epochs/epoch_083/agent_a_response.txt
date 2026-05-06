def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    for tx, ty in res:
        self_d = cheb((sx, sy), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        advantage = opp_d - self_d  # positive means we arrive sooner (or same if 0)
        # Prefer: clear advantage, then quicker pick, then closer relative position
        key = (advantage, -self_d, -opp_d, -((tx + 3*ty) % 7), tx, ty)
        if best is None or key > best[0]:
            best = (key, (tx, ty))

    _, (tx, ty) = best

    # Choose move that maximizes improvement; if tie, lexicographic by dx,dy order above.
    curr_d = cheb((sx, sy), (tx, ty))
    best_move = (0, 0)
    best_score = (-10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb((nx, ny), (tx, ty))
        step_adv = cheb((ox, oy), (tx, ty)) - nd
        # primary: maximize step_adv and reduce nd; secondary: break ties deterministically
        score = (step_adv, -(nd - curr_d), -abs(nx - ox), -abs(ny - oy), dx, dy)
        if best_score[1] is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]