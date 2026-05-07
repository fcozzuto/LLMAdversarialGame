def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target selection: maximize how much closer we are (diagonal-friendly), then speed, then tie-break deterministically.
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive => we are closer/equal
        # Small preference to avoid "stale" targets: prefer smaller sd when lead is tied
        toward = (rx - sx) * (rx - ox) + (ry - sy) * (ry - oy)
        # Deterministic tie-break: lexicographic based on coordinates
        key = (lead, -sd, toward, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    # One-step lookahead: among legal neighboring moves, pick that improves distance race to chosen target.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    ranked = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        score = (nod - nsd, -nsd, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
        ranked.append((score, [dx, dy]))
    if ranked:
        ranked.sort(key=lambda t: t[0], reverse=True)
        return ranked[0][1]
    return [0, 0]