def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    # Target: maximize opponent lead gap (op_d - my_d), then prefer nearer resource, then deterministic tie by coords.
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        key = (op_d - my_d, -my_d, -(rx + 10 * ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    deltas = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            score = -10**9
        else:
            my_d_new = cheb(nx, ny, tx, ty)
            op_d_now = cheb(ox, oy, tx, ty)
            lead = op_d_now - my_d_new
            # One-step opportunism: if a resource is adjacent/collectable, reward it.
            collect_bonus = 0
            for rx, ry in resources:
                if cheb(nx, ny, rx, ry) == 0:
                    collect_bonus += 3
                elif cheb(nx, ny, rx, ry) == 1 and (rx == tx and ry == ty):
                    collect_bonus += 1
            # Obstacle avoidance heuristic (local): discourage stepping into squares that are surrounded.
            neigh_block = 0
            for mx, my in deltas[1:]:
                ax = nx + mx
                ay = ny + my
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                    neigh_block += 1
            score = lead * 10 + collect_bonus - neigh_block
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]