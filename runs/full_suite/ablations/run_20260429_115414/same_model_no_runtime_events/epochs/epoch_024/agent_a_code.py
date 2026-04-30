def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_rx, best_ry = None, None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer taking when we're closer; otherwise deny by picking where opponent is close.
        # Key: maximize advantage, then prefer smaller our distance, then prefer smaller resource distance from center.
        adv = do - ds
        center_dist = cheb(rx, ry, (w - 1) / 2.0, (h - 1) / 2.0)
        key = (adv, -ds, -do, -center_dist)
        if best_key is None or key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry
    curd = cheb(sx, sy, tx, ty)

    # Deterministic tie-break order: same as dirs list.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Also consider whether this move keeps us from letting opponent get strictly closer.
        opp_before = cheb(ox, oy, tx, ty)
        opp_after = cheb(ox + (1 if tx > ox else -1 if tx < ox else 0),
                         oy + (1 if ty > oy else -1 if ty < oy else 0), tx, ty)
        m_adv = (opp_after - nd) - (opp_before - curd)
        mkey = (-(nd - curd), m_adv, -nd, -cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0))
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]