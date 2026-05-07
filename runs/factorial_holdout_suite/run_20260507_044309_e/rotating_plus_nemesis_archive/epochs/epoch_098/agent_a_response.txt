def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # No visible resources: head to opponent corner to avoid being forced away
    if not resources:
        tx, ty = (w - 1 if ox < sx else 0), (h - 1 if oy < sy else 0)
        best = [0, 0]
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    # Pick resource with greatest time-advantage (our distance smaller than theirs)
    best_cell = resources[0]
    best_adv = -10**9
    best_selfd = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # Slight tie-break toward cells more central (reduces predictable sweep interception)
        cent = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key_adv = adv - 0.05 * cent
        if key_adv > best_adv + 1e-9 or (abs(key_adv - best_adv) <= 1e-9 and (sd < best_selfd or (sd == best_selfd and (rx, ry) < best_cell))):
            best_adv = key_adv
            best_selfd = sd
            best_cell = (rx, ry)

    tx, ty = best_cell

    # Choose a valid immediate step that minimizes our distance to target; deterministic tie-break by move order
    best_move = [0, 0]
    best_dist = 10**9
    best_opp = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        if sd < best_dist or (sd == best_dist and adv > best_opp) or (sd == best_dist and adv == best_opp and (dx, dy) < (best_move[0], best_move[1])):
            best_dist = sd
            best_opp = adv
            best_move = [dx, dy]
    return best_move