def choose_move(observation):
    me = observation["self_position"]
    opp = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick target resource that gives us best immediate advantage (closer than opponent)
    best_t = None
    best_key = None
    for r in resources:
        rt = tuple(r)
        if rt in obstacles:
            continue
        dm = cheb(me, rt)
        do = cheb(opp, rt)
        # Prefer resources where opponent is relatively farther; tie-break by coordinates
        key = (do - dm, -(dm), -rt[0], -rt[1])
        if best_key is None or key > best_key:
            best_key = key
            best_t = rt

    if best_t is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_t

    # Evaluate candidate moves by expected advantage at next state
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = me[0] + dx, me[1] + dy
        if not valid(nx, ny):
            continue
        nm = (nx, ny)
        myd = cheb(nm, (tx, ty))
        opd = cheb(opp, (tx, ty))

        # Encourage moving closer; discourage giving opponent too much reduction by staying away from their nearest direction
        # Also add mild pressure to get closer to opponent to contest if targets are equal
        contest = cheb(nm, opp)
        val = (opd - myd, -myd, -contest)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]