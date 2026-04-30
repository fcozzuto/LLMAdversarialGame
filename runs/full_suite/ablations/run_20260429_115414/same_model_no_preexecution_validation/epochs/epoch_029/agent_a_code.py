def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                valid_res.append((x, y))

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]

    if not valid_res:
        # fallback: head toward farthest-from-opponent corner
        corners = [(0, 0),(0, h-1),(w-1, 0),(w-1, h-1)]
        best = (0, 0); bestv = -10**18
        for tx, ty in corners:
            v = cheb(sx, sy, tx, ty) * -1 + cheb(ox, oy, tx, ty)
            if v > bestv:
                bestv = v; best = (tx, ty)
        tx, ty = best
    else:
        best = valid_res[0]; bestv = -10**18
        for tx, ty in valid_res:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # prefer closer to us, farther from opponent; add slight tie-break toward higher x,y
            v = (do * 2 - ds * 3) + (tx * 0.01) + (ty * 0.001)
            if v > bestv:
                bestv = v; best = (tx, ty)
        tx, ty = best

    # choose step reducing distance to target and avoiding obstacles
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        # small penalty if moving away from target
        improvement = (cheb(sx, sy, tx, ty) - ds2)
        v = improvement * 10 + (do2 * 2 - ds2 * 3) - (abs(dx) + abs(dy)) * 0.001
        # deterministic tie-break
        v += (dx + 1) * 1e-6 + (dy + 1) * 1e-9
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]