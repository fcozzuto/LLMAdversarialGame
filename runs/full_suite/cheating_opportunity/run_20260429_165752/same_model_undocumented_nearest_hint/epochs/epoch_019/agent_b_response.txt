def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # Decide among immediate moves by choosing the resource that maximizes our advantage,
    # with extra pressure to reduce opponent's closest approach.
    best_move = (0, 0)
    best_score = -10**18

    # Precompute opponent min distance to each resource (static per turn)
    opp_dist = {}
    for rx, ry in resources:
        opp_dist[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        # Evaluate move: best target for us + deterrent on opponent for that target.
        move_score = -10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = opp_dist[(rx, ry)]

            # Prefer targets we can reach sooner than opponent, otherwise still prefer
            # large gaps in (opponent - self). If tied, steer toward smaller self distance.
            gap = d_opp - d_self
            val = 1000 * gap - 3 * d_self

            # If we are closer than opponent, heavily reward; else mild penalty.
            if gap >= 0:
                val += 800
            else:
                val -= 200 * (-gap)

            # Encourage moving toward the "frontier" direction (toward opponent/opposite corner)
            # to diversify when no winning gap exists.
            border_bias = (cheb(nx, ny, W - 1, H - 1) - cheb(ox, oy, W - 1, H - 1))
            val -= 2 * border_bias

            if val > move_score:
                move_score = val

        # Small penalty for staying still unless it gives the best immediate target advantage.
        if dxm == 0 and dym == 0:
            move_score -= 15

        if move_score > best_score:
            best_score = move_score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]