def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = resources[:]
    if not targets:
        targets = [(w // 2, h // 2)]
    else:
        # Keep determinism and limit work: choose up to 6 best candidates from our perspective.
        # Also ensures we react when resources are few.
        scored = [(md(sx, sy, x, y), x, y) for (x, y) in targets]
        scored.sort(key=lambda t: (t[0], t[1], t[2]))
        targets = [(x, y) for _, x, y in scored[:6]]

    best = None
    ti = int(observation.get("turn_index", 0) or 0)
    corner_bias = 1 if (sx + sy + ti) % 2 == 0 else -1

    for dx, dy, nx, ny in legal:
        # Evaluate move by best contest advantage among candidate targets.
        # Advantage: opponent closer -> bad; we want (opp_dist - self_dist) large.
        best_adv = -10**9
        best_tx, best_ty = 0, 0
        for (tx, ty) in targets:
            ds = md(nx, ny, tx, ty)
            do = md(ox, oy, tx, ty)
            # Encourage moving toward the board diagonal that helps us reach more resources early.
            diag = (tx - sx) + (ty - sy)
            adv = (do - ds) * 10 + (diag // 3) * corner_bias
            if adv > best_adv or (adv == best_adv and (tx, ty) < (best_tx, best_ty)):
                best_adv = adv
                best_tx, best_ty = tx, ty

        # Small preference for reducing our distance to the chosen target and staying safe-ish.
        ds_to = md(nx, ny, best_tx, best_ty)
        # Tie-break deterministically by move direction order.
        score = (best_adv, -ds_to, dx, dy)
        if best is None or score > best[0]:
            best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]