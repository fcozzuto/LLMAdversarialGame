def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def dist(a, b, c, d):
        ad = a - c
        if ad < 0:
            ad = -ad
        bd = b - d
        if bd < 0:
            bd = -bd
        return ad + bd

    # Choose a target where we have advantage; break ties by smaller self distance.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        key = (od - sd, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # One-step lookahead with obstacle avoidance; deterministic tie-break.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            nsd = dist(nx, ny, tx, ty)
            nod = dist(ox, oy, tx, ty)
            # Prefer approaching target and increasing advantage; slight penalty for staying still.
            move_pen = 0 if (dx == 0 and dy == 0) else 0
            key = (nod - nsd, -nsd, -(abs(tx - nx) + abs(ty - ny)), -move_pen, dx, dy)
            candidates.append((key, [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]