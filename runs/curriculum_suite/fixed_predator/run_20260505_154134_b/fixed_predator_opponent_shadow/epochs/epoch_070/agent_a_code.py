def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

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

    def target_key(cx, cy):
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        return (od - sd, -sd, -cx, -cy)

    # Prefer a target where we aren't significantly behind; fall back if all lead.
    scored = [(target_key(cx, cy), (cx, cy)) for cx, cy in resources]
    scored.sort(key=lambda t: t[0], reverse=True)
    best_t = scored[0][1]
    best_key = scored[0][0]
    # If opponent is very close to best target, try to find a contested one where we can at least tie.
    if best_key[0] < -1:
        for k, (cx, cy) in scored[1:]:
            if k[0] >= -1:
                best_t = (cx, cy)
                break
        # else keep best_t

    tx, ty = best_t

    best_move = [0, 0]
    best_val = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            my_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Maximize our advantage; prioritize reaching the target and avoiding ties that keep us far.
            val = (opp_d - my_d, -my_d, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move