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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cent(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        dx = x - cx
        if dx < 0: dx = -dx
        dy = y - cy
        if dy < 0: dy = -dy
        return dx + dy

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # prefer states where opponent is further
        key = (gap, -sd, -cent(rx, ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    best_move = [0, 0]
    best_md = None
    best_ms = None
    # deterministic tie-break by fixed iteration order
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            md = cheb(nx, ny, tx, ty)
            # small bias to worsen opponent's relative progress
            opp_sd = cheb(ox, oy, tx, ty)
            my_adv = opp_sd - md
            ms = (my_adv, -md, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if best_md is None or ms > best_ms:
                best_md = md
                best_ms = ms
                best_move = [dx, dy]
    return best_move if best_md is not None else [0, 0]