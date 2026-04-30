def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    cx, cy = (W - 1) // 2, (H - 1) // 2
    best_move = legal[0]
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            self_best = 10**9
            opp_best_for_self_best = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # prioritize resources we can reach earlier than opponent
                if ds < self_best or (ds == self_best and do > opp_best_for_self_best):
                    self_best = ds
                    opp_best_for_self_best = do
            # advantage: how much closer we are (in Chebyshev) than opponent to the same chosen resource
            score = (opp_best_for_self_best - self_best)
            # mild tie-break: go towards center, avoid excessive distance to nearest resource
            d_center = abs(nx - cx) + abs(ny - cy)
            score -= 0.01 * d_center
            # and strongly prefer immediate resource pickup
            if (nx, ny) in resources:
                score += 5.0
        else:
            # no resources: just move toward center
            score = -(abs(nx - cx) + abs(ny - cy))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]