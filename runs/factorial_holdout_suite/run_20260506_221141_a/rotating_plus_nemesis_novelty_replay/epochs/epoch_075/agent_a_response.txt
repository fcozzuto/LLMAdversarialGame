def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py): obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                resources.append((rx, ry))

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise pick those minimizing opponent lead.
        lead = do - ds
        # Deterministic tie-break: prefer lower coordinates.
        key = (lead > 0, -lead, ds, rx, ry)  # reachable first, then reduce opponent advantage, then closer
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((cd(sx, sy, tx, ty), 1, dx, dy))
            else:
                if inb(nx, ny) and (nx, ny) not in obs:
                    # Minimize distance-to-target, then keep movement deterministic.
                    moves.append((cd(nx, ny, tx, ty), 0, dx, dy))
    # Prefer moving (0 over 1 flag), then smaller distance, then fixed ordering.
    moves.sort(key=lambda t: (t[1], t[0], t[2], t[3]))
    return [int(moves[0][2]), int(moves[0][3])]