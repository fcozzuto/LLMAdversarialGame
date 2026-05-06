def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    def target_key(cell):
        cx, cy = cell
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        # Prefer: we are not too far, and the opponent is relatively farther.
        lead = self_d - opp_d  # negative means opponent closer
        # If opponent is closer, heavily prefer locations where we can catch quickly.
        catch_bonus = (lead >= 0) * 200
        return (catch_bonus - lead, -self_d, -cheb(ox, oy, cx, cy), -cx, -cy)

    tx, ty = resources[0]
    bestk = None
    for r in resources:
        k = target_key(r)
        if bestk is None or k > bestk:
            bestk = k
            tx, ty = r

    def eval_pos(nx, ny):
        # Heuristic: get closer to target, move so opponent stays farther from it.
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If the opponent could reach target next, improve by making ourselves closer than them.
        lead = self_d - opp_d
        return (-self_d, lead, -cheb(nx, ny, ox, oy), (nx == tx and ny == ty))

    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            sc = eval_pos(nx, ny)
            if best_score is None or sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]