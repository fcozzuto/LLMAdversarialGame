def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # deterministic exploration parity
        tx, ty = (0, 0) if ((ox + oy + observation.get("turn_index", 0)) & 1) == 0 else (w - 1, h - 1)
    else:
        best_lead = None
        best_block = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            key_lead = (lead, -ds, -(abs(rx - ox) + abs(ry - oy)), rx, ry)
            if best_lead is None or key_lead > best_lead[0]:
                best_lead = (key_lead, rx, ry)
            # blocking: choose resource opponent is closest to (most negative lead)
            key_block = (-do, ds, -lead, rx, ry)
            if best_block is None or key_block > best_block[0]:
                best_block = (key_block, rx, ry)

        # if we can be first on some resource, take best lead; else block opponent's closest
        if best_lead[0][0] > 0:
            tx, ty = best_lead[1], best_lead[2]
        else:
            tx, ty = best_block[1], best_block[2]

    # choose move that reduces our distance to (tx,ty) while avoiding obstacles
    curd = cheb(sx, sy, tx, ty)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # secondary: don't step into cells that are closer for opponent to the same target (helps contest)
        ndo = cheb(ox, oy, tx, ty)
        key = (-(nd - curd), -nd, (ndo - cheb(ox, oy, tx, ty)), abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]