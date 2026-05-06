def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

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

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def best_opp_pos(tx, ty):
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, -dx, -dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (nx, ny)
        return best if best is not None else (ox, oy)

    def opp_d_after(tx, ty):
        px, py = best_opp_pos(tx, ty)
        return cheb(px, py, tx, ty)

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # choose target that maximizes our advantage given opponent predicted move
        local_best = None
        local_key = None
        for tx, ty in resources:
            self_d = cheb(nx, ny, tx, ty)
            o_d = opp_d_after(tx, ty)
            adv = o_d - self_d
            key = (adv, -self_d, -tx, -ty)
            if local_key is None or key > local_key:
                local_key = key
                local_best = (tx, ty, self_d, o_d)
        if local_key is None:
            continue
        # prefer higher advantage, then being closer, then deterministic tie-break on move
        _, self_d, o_d = local_best[0], local_best[2], local_best[3]
        move_key = (local_key[0], -self_d, -o_d, dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]