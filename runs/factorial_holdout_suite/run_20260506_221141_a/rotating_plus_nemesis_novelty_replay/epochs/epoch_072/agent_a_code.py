def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    def mdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    best_t = None
    best_k = None
    for tx, ty in resources:
        sd = mdist(sx, sy, tx, ty)
        od = mdist(ox, oy, tx, ty)
        k = (od - sd, -sd, tx, ty)
        if best_k is None or k > best_k:
            best_k, best_t = k, (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = None
    cand_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd = mdist(nx, ny, tx, ty)
        od = mdist(ox, oy, tx, ty)
        # Prefer moves that increase "arrival advantage", then get closer, then keep progress deterministic.
        k = (od - sd, -sd, -abs(nx - tx) - abs(ny - ty), nx, ny)
        if cand_k is None or k > cand_k:
            cand_k, cand = k, (dx, dy)

    if cand is None:
        return [0, 0]
    return [int(cand[0]), int(cand[1])]