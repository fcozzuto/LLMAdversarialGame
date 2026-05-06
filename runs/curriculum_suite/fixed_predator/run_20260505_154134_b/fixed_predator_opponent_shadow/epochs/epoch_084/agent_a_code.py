def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))

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

    def pick_target():
        best = None
        best_key = None
        for cx, cy in resources:
            self_d = cheb(sx, sy, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # contested: prefer where opponent is closer than us, but also keep progress for us
            key = (opp_d - self_d, -self_d, -((cx << 3) ^ cy))
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    tx, ty = pick_target()

    cand_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                cand_moves.append((dx, dy))

    if not cand_moves:
        return [0, 0]

    best_mv = None
    best_key = None
    for dx, dy in cand_moves:
        nx, ny = sx + dx, sy + dy
        self_next = cheb(nx, ny, tx, ty)
        self_now = cheb(sx, sy, tx, ty)
        opp_next = cheb(nx, ny, ox, oy)

        # prefer reducing distance to target; if equal, prefer increasing separation from opponent;
        # also prefer moves that don't "back away" (deterministic tie-breakers)
        key = (self_now - self_next, -self_next, opp_next, -abs(dx), -abs(dy), (dx, dy) )
        if best_key is None or key > best_key:
            best_key = key
            best_mv = [dx, dy]

    return best_mv