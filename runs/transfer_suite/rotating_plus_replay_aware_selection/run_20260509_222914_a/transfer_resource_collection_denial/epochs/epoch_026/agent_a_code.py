def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        # Fall back to center-ish, but avoid obstacles
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if best is None or d < best[0] or (d == best[0] and (nx, ny) < best[1]):
                best = (d, (nx, ny))
        return [best[1][0] - x, best[1][1] - y] if best else [0, 0]

    # If we stand on a resource, stay to secure it deterministically.
    if (x, y) in set(res):
        return [0, 0]

    # Choose move that maximizes capture advantage over opponent for the best reachable resource.
    best_move = None  # (score, nx, ny)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # Evaluate best target for this move
        best_adv_for_move = None
        best_res_for_move = None
        myd0 = md(nx, ny, ox, oy)
        # Prefer moving away from opponent slightly to avoid immediate contest
        for rx, ry in res:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            # Advantage: positive means we are closer than opponent to that resource
            adv = (oppd - myd) * 10 - myd
            # Small tie-breakers: reduce distance to resource but also prefer moving toward it rather than opponent
            adv -= 0.05 * myd0
            if best_adv_for_move is None or adv > best_adv_for_move or (adv == best_adv_for_move and (myd, (rx, ry)) < (md(x, y, best_res_for_move[0], best_res_for_move[1]) if best_res_for_move else 10**9, best_res_for_move if best_res_for_move else (999, 999))):
                best_adv_for_move = adv
                best_res_for_move = (rx, ry)

        # Overall: maximize advantage; tie-break by closer to best target; then deterministic by position
        if best_adv_for_move is None:
            continue
        myd_best = md(nx, ny, best_res_for_move[0], best_res_for_move[1])
        score = best_adv_for_move
        if best_move is None or score > best_move[0] or (score == best_move[0] and (myd_best, nx, ny) < (best_move[1], best_move[2], best_move[3])):
            best_move = (score, myd_best, nx, ny)

    if best_move is None:
        return [0, 0]
    return [best_move[2] - x, best_move[3] - y]