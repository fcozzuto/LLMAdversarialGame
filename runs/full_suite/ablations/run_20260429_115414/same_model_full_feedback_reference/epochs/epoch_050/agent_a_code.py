def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = (W // 2), (H // 2)
    else:
        # Contest resources where we can gain the most (self closer than opponent).
        best = None
        best_score = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer positive swing; also slightly penalize far resources to reduce dithering.
            score = (do - ds) * 10 - ds
            # Deterministic tie-break: lower coord sum first
            if score > best_score or (score == best_score and (rx + ry, rx, ry) < (best[0] + best[1], best[0], best[1])):
                best_score = score
                best = (rx, ry)
        tx, ty = best

    # One-step greedy: reduce distance to target, but also avoid letting opponent reduce theirs.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        # Compare "after-move" advantage, with tie-break on proximity to opponent (disrupt when close).
        my_adv = op_d - my_d
        val = my_adv * 1000 - my_d * 3 - cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move