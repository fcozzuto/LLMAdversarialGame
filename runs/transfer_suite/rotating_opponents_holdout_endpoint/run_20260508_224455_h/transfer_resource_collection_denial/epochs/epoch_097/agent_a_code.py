def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        x, y = p
        obs.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    # Chebyshev distance matches diagonal movement well
    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pre-filter resources not on obstacles
    res = []
    for r in resources:
        x, y = r
        ix, iy = int(x), int(y)
        if inb(ix, iy) and (ix, iy) not in obs:
            res.append((ix, iy))
    if not res:
        return [0, 0]

    # Keep evaluation small but deterministic
    res.sort(key=lambda p: dist((sx, sy), p))
    res = res[:10]

    best_move = (0, 0)
    best_score = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Obstacle repulsion: discourage stepping adjacent to obstacles
        rep = 0
        for oxp, oyp in obstacles:
            if abs(nx - int(oxp)) <= 1 and abs(ny - int(oyp)) <= 1:
                rep -= 3

        # Evaluate this move by how much it can undercut opponent on some resource
        move_score = rep
        next_self = (nx, ny)

        # For efficiency, use only top few closest-for-opponent resources
        scored = 0
        for r in res:
            ds = dist(next_self, r)
            do = dist((ox, oy), r)
            # Want ds < do; also reduce ds and prefer larger lead opportunities
            val = (do - ds) * 10 - ds
            if ds == 0:
                val += 1000  # immediate collection priority
            # Mild preference to stay near best "contested" direction
            move_score += val
            scored += 1
            if scored >= 5:
                break

        # Tie-break: prefer moves that also reduce distance to nearest resource
        if best_score < move_score:
            best_score = move_score
            best_move = (dxm, dym)
        elif best_score == move_score:
            dcur = dist((sx, sy), res[0])
            dnxt = dist((nx, ny), res[0])
            bdcur = dist((sx, sy), res[0])
            bdx, bdy = best_move
            bnx, bny = sx + bdx, sy + bdy
            bdnxt = dist((bnx, bny), res[0])
            if (bdcur - bdnxt) < (dcur - dnxt):
                best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]