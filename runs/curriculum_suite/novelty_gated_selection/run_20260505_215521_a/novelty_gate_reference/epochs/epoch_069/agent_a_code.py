def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Strategy: for each candidate move, maximize "positional advantage" on the best contested resource,
    # and add a penalty when the opponent is already closer (or ties) to the same resource.
    best_key = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate after move: compute best advantage across resources.
        # advantage = (opp_dist - my_dist); we want it large.
        # penalty if opponent would have a non-worse distance to that target (discourage chase into their lane).
        best_adv = -10**9
        best_pen = 10**9
        best_res = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            # tie/behind opponent penalty:
            pen = 0
            if opd <= myd:
                pen = (myd - opd) + 1  # >0 if we're not strictly closer
            # prefer closer resource cluster (small myd) if advantages equal
            tie = (adv == best_adv)
            if adv > best_adv or (adv == best_adv and (pen < best_pen or (pen == best_pen and myd < cheb(sx, sy, rx, ry)))):
                best_adv = adv
                best_pen = pen
                best_res = (rx, ry)

        # Additional shaping: avoid "giveaway" where we move into being closer to many resources
        # that opponent also can reach quickly (keeps more control).
        # Deterministic: compute control margin on top 3 resources by adv from this move.
        scored = []
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            scored.append((opd - myd, -myd))
        scored.sort(reverse=True)
        ctrl = 0
        for i in range(min(3, len(scored))):
            ctrl += scored[i][0]

        # Key: primary maximize best_adv, then maximize ctrl, then minimize pen, then deterministic move order.
        move_order = (dx, dy)
        key = (best_adv, ctrl, -best_pen, -cheb(nx, ny, best_res[0], best_res[1]) if best_res else 0, move_order)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]