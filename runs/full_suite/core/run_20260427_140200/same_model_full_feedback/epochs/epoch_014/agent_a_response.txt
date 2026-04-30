def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            score = -cheb(nx, ny, ox, oy)
            key = (score, cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key > best:
                best = key
        return [best[2], best[3]]

    best_key = None
    # Evaluate by choosing a target resource maximizing our advantage over the opponent.
    # Advantage is opp_dist - self_dist after our candidate move.
    for dx, dy, nx, ny in legal:
        best_adv = -10**9
        best_tdist = 10**9
        best_tx = 0
        best_ty = 0
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd
            # Slightly prefer nearer targets when advantage is similar.
            tieb = sd
            if adv > best_adv or (adv == best_adv and tieb < best_tdist) or (adv == best_adv and tieb == best_tdist and (tx, ty) < (best_tx, best_ty)):
                best_adv = adv
                best_tdist = sd
                best_tx, best_ty = tx, ty
        # Deterrence against walking away: penalize large distance to opponent slightly.
        opp_d = cheb(nx, ny, ox, oy)
        key = (best_adv, -best_tdist, -opp_d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key

    return [best_key[3], best_key[4]]