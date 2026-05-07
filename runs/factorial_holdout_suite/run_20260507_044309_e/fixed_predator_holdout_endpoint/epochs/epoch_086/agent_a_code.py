def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    turns_remaining = int(observation.get("turns_remaining") or 0)

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        if ds > turns_remaining + 2:
            continue
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise go for best swing.
        we_win = 1 if ds <= do else 0
        key = (we_win, do - ds, -ds, -abs(rx - ox) - abs(ry - oy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
    else:
        rx, ry = best

    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    return [dx, dy]