def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        # fallback: head toward center while avoiding obstacles
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            dcent = cheb(nx, ny, cx, cy)
            key = (dcent, cheb(nx, ny, ox, oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    res = [(r[0], r[1]) for r in resources]

    def best_dist(px, py):
        dmin = None
        dsecond = None
        for rx, ry in res:
            if (rx, ry) in occ:
                continue
            d = cheb(px, py, rx, ry)
            if dmin is None or d < dmin:
                dsecond = dmin
                dmin = d
            elif dsecond is None or d < dsecond:
                dsecond = d
        if dmin is None:
            dmin = cheb(px, py, cx, cy)
            dsecond = dmin
        return dmin, dsecond

    cur_sd, cur_s2 = best_dist(sx, sy)
    cur_od, cur_o2 = best_dist(ox, oy)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        nds, nds2 = best_dist(nx, ny)
        # opponent reacts imperfectly; we still compare our progress vs their current pressure
        adv = cur_od - nds  # positive good: we close gap to nearest resource
        # Secondary heuristic: also reduce their likely advantage if their nearest resource is "revealed"
        # Approx: compare us and opponent nearest distances to resources around our position.
        local_penalty = 0
        for rx, ry in res:
            if (rx, ry) in occ:
                continue
            myd = cheb(nx, ny, rx, ry)
            if myd <= nds and cheb(ox, oy, rx, ry) <= cur_od:
                # if we are picking a resource that is also near opponent, slightly penalize
                if myd == nds:
                    local_penalty += 1

        # tie-break deterministically: closer to center, then smaller opponent-nearability
        key = (-adv, nds, local_penalty, cheb(nx, ny, cx, cy), cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]