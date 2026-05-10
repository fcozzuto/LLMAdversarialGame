def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    if not resources:
        t = int(observation.get("turn_index", 0) or 0)
        tx, ty = (0, 0) if (t & 1) == 0 else (w - 1, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer taking resources we can reach no later than opponent; break ties by quickness and safety.
        lead = do - ds
        dist_line = abs(rx - sx) + abs(ry - sy)
        risk = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = rx + ax, ry + ay
            if (nx, ny) in obstacles:
                risk += 1
        key = (lead, -(-ds), -(dist_line), -risk, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    moves = []
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, cheb(nx, ny, tx, ty)))
    if not moves:
        for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                moves.append((dx, dy, cheb(nx, ny, tx, ty)))

    # Deterministic: minimize distance-to-target; among ties prefer not deviating from opponent race (lead gain).
    bestm = None
    for dx, dy, dnew in moves:
        nx, ny = sx + dx, sy + dy
        ds_new = dnew
        do = cheb(ox, oy, tx, ty)
        lead_new = do - ds_new
        tie = (lead_new, -ds_new, abs(nx - ox) + abs(ny - oy), dx, dy)
        if bestm is None or tie > bestm[0]:
            bestm = (tie, dx, dy)
    return [int(bestm[1]), int(bestm[2])]