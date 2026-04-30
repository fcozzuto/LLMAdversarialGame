def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb((nx, ny), (tx, ty))
            key = (-d, cheb((nx, ny), (ox, oy)) - cheb((sx, sy), (ox, oy)))
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    opp = (ox, oy)
    me = (sx, sy)
    best_r = None
    best_key = None
    for r in resources:
        if r in obstacles:
            continue
        dm = cheb(me, r)
        do = cheb(opp, r)
        key = (do - dm, -do, -dm, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    cur_do = cheb(opp, (sx, sy))
    best = None
    for dx, dy, nx, ny in legal:
        dm_new = cheb((nx, ny), (tx, ty))
        do_new = cheb(opp, (tx, ty))
        key = (do_new - dm_new, -dm_new, -cheb((nx, ny), opp), -((nx, ny) != opp and cheb((nx, ny), opp) < cur_do))
        if best is None or key > best[0]:
            best = (key, (dx, dy))
    return best[1] if best else [0, 0]