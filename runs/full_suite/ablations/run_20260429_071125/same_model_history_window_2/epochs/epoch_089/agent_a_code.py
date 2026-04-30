def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose best target resource considering relative access (deterministic tie-break)
    target = None
    if resources:
        best = None
        for tx, ty in resources:
            d_self = cheb(sx, sy, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Prefer resources we reach sooner; if not, prefer ones that reduce opponent advantage
            key = (d_self - d_opp, d_self, (tx * 31 + ty))
            if best is None or key < best:
                best = key
                target = (tx, ty)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = target
    # If opponent is strictly closer, bias toward reducing their access by moving closer to the same target
    # (still deterministic and legal; ties resolved by move ordering)
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_after = cheb(nx, ny, tx, ty)
        do_after = cheb(ox, oy, tx, ty)  # opponent stays for evaluation (no path info)
        # Score: prioritize reaching target, then blocking via lowering our distance while not moving away from opponent-competition
        # Small bias: also prefer keeping central-ish progress deterministically via coordinate sum.
        central_bias = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
        score = (0, ds_after, -do_after, central_bias, dx, dy) if ds_after != do_after else (1, ds_after, -do_after, central_bias, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]