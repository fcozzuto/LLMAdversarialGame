def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def king(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Prefer staying safe while drifting toward center
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = (10**9, -10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = king(nx, ny, tx, ty)
            if (d, -(nx + ny)) < (best[0], best[1]):
                best = (d, -(nx + ny), dx, dy)
        return [best[2], best[3]]

    # Choose target by "capture advantage": how much closer we are than opponent (king distance)
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = king(sx, sy, rx, ry)
        od = king(ox, oy, rx, ry)
        # Prefer largest (od - sd); tie-break by smaller sd, then by position
        key = (od - sd, -sd, -(rx * 17 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    # Take step that maximizes advantage after move; primary minimize distance to target
    best_move = (10**9, -10**9, 0, 0)  # (dist_to_target, -adv, -sum, dxdy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = king(nx, ny, rx, ry)
        adv = king(ox, oy, rx, ry) - nd
        tie = -(nx + ny)
        cand = (nd, -adv, tie, dx, dy)
        if cand < best_move:
            best_move = cand

    return [best_move[3], best_move[4]]