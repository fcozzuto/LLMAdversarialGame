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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    score_map = observation.get("scores") or {}
    sa = None
    if isinstance(score_map, dict):
        sa = score_map.get(observation.get("self_name"))
        sb = score_map.get(observation.get("opponent_name"))
    else:
        sb = None
    if sa is None or sb is None:
        behind = True
    else:
        behind = float(sa) < float(sb)  # if behind, force sharper contest

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            continue

        best_adv = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer than opponent
            # When behind, prioritize moves that create contest immediately; otherwise just maximize advantage.
            if behind:
                adv = adv * 2 - myd * 0.15
            key_adv = adv
            if key_adv > best_adv + 1e-12 or (abs(key_adv - best_adv) <= 1e-12 and myd < best_dist):
                best_adv = key_adv
                best_dist = myd

        # tie-break deterministically: prefer smaller best_dist then prefer moves closer to opponent direction
        opp_dir = (ox - sx)
        dir_bias = abs(opp_dir)  # harmless deterministic tie-break
        key = (-best_adv, best_dist, dir_bias, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]