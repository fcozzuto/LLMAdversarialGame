def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a resource where we are (relatively) closer than the opponent.
    best_t = None
    best_adv = None
    best_ds = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = ds - do  # smaller is better (more negative means we're closer)
        if best_t is None or adv < best_adv or (adv == best_adv and ds < best_ds) or (adv == best_adv and ds == best_ds and (tx, ty) < best_t):
            best_t = (tx, ty)
            best_adv = adv
            best_ds = ds

    tx, ty = best_t

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_adj(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                ny = y + ddy
                if ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    c += 1
        return c

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Main objective: minimize distance to chosen target.
        # Secondary: keep some distance from opponent, avoid obstacle-clutter.
        val = (-10 * d_to_t) + (d_to_o) - (3 * obst_adj(nx, ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move