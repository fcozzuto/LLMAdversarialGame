def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx = 0 if ox > (w - 1) / 2 else w - 1
        ty = 0 if oy > (h - 1) / 2 else h - 1
        best_m = (0, 0)
        best_v = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer moving away from opponent and toward the opposite corner
            v = -cheb(nx, ny, ox, oy) + (-cheb(nx, ny, tx, ty))
            if v > best_v:
                best_v, best_m = v, (dx, dy)
        return [best_m[0], best_m[1]]

    # Deny: pick moves that improve relative advantage at the same best resource
    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # choose a target resource deterministically by best relative advantage after this move
        best_rel = 10**9
        best_tid = None
        for i, (tx, ty) in enumerate(resources):
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            rel = sd - od  # smaller => we are closer than opponent
            if rel < best_rel or (rel == best_rel and (best_tid is None or (tx, ty) < resources[best_tid])):
                best_rel = rel
                best_tid = i
        # Score: primary minimize relative disadvantage; secondary minimize our distance; tertiary maximize separation after step
        tx, ty = resources[best_tid]
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(nx, ny, ox, oy)
        v = (-best_rel) * 1000 - my_d * 3 + op_d
        if v > best_v:
            best_v, best_m = v, (dx, dy)

    return [best_m[0], best_m[1]]