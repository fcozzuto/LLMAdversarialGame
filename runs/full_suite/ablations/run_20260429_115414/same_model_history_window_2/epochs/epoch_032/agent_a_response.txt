def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = len(resources)

    if not resources or rem <= 0:
        tx, ty = w - 1, h - 1
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, tx, ty) + 0.01 * cheb(nx, ny, ox, oy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose move that improves our advantage over opponent for the best contested target.
    best = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        # Evaluate our best target under this hypothetical position.
        best_adv = None
        for tx, ty in resources:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Higher when we are closer than opponent; small tie-breaker by total distance.
            adv = (d_opp - d_self) * 10 - man(nx, ny, tx, ty)
            if best_adv is None or adv > best_adv:
                best_adv = adv
        # Encourage staying away from opponent when resources are far.
        v = -best_adv + 0.03 * cheb(nx, ny, ox, oy)
        if best is None or v < best[0]:
            best = (v, dxm, dym)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]