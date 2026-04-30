def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_from(posx, posy):
        if not resources:
            tx, ty = int(round(cx)), int(round(cy))
            ds = cheb(posx, posy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            return (do - ds, -ds, -abs(posx - cx) - abs(posy - cy), -posx, -posy)

        best = None
        for tx, ty in resources:
            ds = cheb(posx, posy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            center_bias = -(abs(tx - cx) + abs(ty - cy))
            # Prefer targets where we are closer than opponent; then closer; then toward center; then deterministic tie-break.
            key = (do - ds, -ds, center_bias, -tx, -ty)
            if best is None or key > best:
                best = key
        return best

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        key = score_from(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]