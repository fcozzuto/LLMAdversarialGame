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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    cx = (W - 1) // 2
    cy = (H - 1) // 2
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            k = (-d, -cheb(nx, ny, ox, oy))
            if best is None or k > best[0]:
                best = (k, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Evaluate how much this move improves our best contested resource this turn/soon.
        best_score = None
        best_min_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Prefer resources we can reach sooner than opponent; heavily penalize where opponent is no farther.
            # Deterministic: use integer arithmetic by scaling penalty.
            lead = do - ds  # positive is good
            block = 2 if do <= ds else 0  # if opponent can match/beat, penalize
            score = lead * 10 - block * 3

            if best_score is None or score > best_score or (score == best_score and ds < best_min_ds):
                best_score = score
                best_min_ds = ds

        # Secondary: tie-break with overall closeness to chosen resource and away from opponent.
        key = (best_score, -best_min_ds, -cheb(nx, ny, ox, oy), -cheb(nx, ny, cx, cy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]