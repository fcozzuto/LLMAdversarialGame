def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target_list = resources if resources else [(ox, oy)]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer moves that increase capture advantage on the best available resource.
        best_adv = None
        best_ds = None
        best_to_opp = None
        for tx, ty in target_list:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            adv = do - ds  # positive means we can arrive no later (in chebyshev steps)
            if best_adv is None or (adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and do < best_to_opp)))):
                best_adv = adv
                best_ds = ds
                best_to_opp = do

        # Secondary pressure: don't let opponent get strictly closer to its nearest resource than we would.
        # (Approximate via comparing distances to the nearest resource from each side after our move.)
        opp_near = 10**9
        self_near = 10**9
        for tx, ty in (resources if resources else [(ox, oy)]):
            dd_s = cheb(nx, ny, tx, ty)
            dd_o = cheb(ox, oy, tx, ty)
            if dd_s < self_near:
                self_near = dd_s
            if dd_o < opp_near:
                opp_near = dd_o
        # If we move near a resource but also dramatically increase opponent's chance (lower opp_near),
        # penalize slightly.
        key = (best_adv, -(self_near - opp_near), -best_ds, -best_to_opp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]