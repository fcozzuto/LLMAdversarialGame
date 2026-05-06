def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
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

    def pick_target():
        if not resources:
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # primary: maximize (opp closer than us) by making opp_d-self_d large
            # secondary: prefer closer (smaller self_d)
            # tertiary: deterministic tie by coordinates
            key = (opp_d - self_d, -self_d, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    def move_candidates():
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obs:
                    out.append((dx, dy))
        if not out:
            out = [(0, 0)]
        return out

    target = pick_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    cands = move_candidates()
    best_move = (0, 0)
    best_key = None
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # greedy improvement: maximize advantage, then minimize self_d after move
        key = (opp_d - self_d, -self_d, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]