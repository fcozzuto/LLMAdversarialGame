def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best_move = (0, 0)
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: (cheb(ox, oy, p[0], p[1]), -p[0], -p[1]))
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) != best_move):
                bestd = d
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose target with maximum current advantage (self closer than opponent)
    # Advantage = dist_op - dist_self; pick highest; break ties by closer self.
    best_res = None
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and (ds < best_selfd or (ds == best_selfd and (rx, ry) < best_res))):
            best_adv = adv
            best_selfd = ds
            best_res = (rx, ry)

    rx, ry = best_res

    # Evaluate moves by resulting advantage to the chosen target; slight preference to also reduce opponent distance.
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        adv2 = do2 - ds2
        # Small tie-breakers: prefer smaller ds2; and prefer moving away from opponent if equal.
        score = adv2 * 1000 - ds2 * 3 - cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]