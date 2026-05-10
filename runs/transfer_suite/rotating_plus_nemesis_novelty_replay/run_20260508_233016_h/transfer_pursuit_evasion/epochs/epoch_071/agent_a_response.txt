def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    opp_role = str(observation.get("opponent_role") or "")
    self_evader = "evader" in self_role.lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cx, cy = w // 2, h // 2

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    tx, ty = target_corner

    def score(nx, ny):
        # pursuer: maximize capture likelihood => minimize distance; also prefer approaching aligned (cut-off).
        # evader: maximize distance; also prefer drifting toward the far corner while avoiding corner trap near obstacles.
        d2 = dist2(nx, ny, ox, oy)
        man = abs(nx - ox) + abs(ny - oy)
        align = (0 if nx == ox else 1) + (0 if ny == oy else 1)  # 0 means perfectly aligned in both axes
        toward_corner = -dist2(nx, ny, tx, ty) if self_evader else dist2(nx, ny, tx, ty)
        # obstacle proximity penalty (local)
        prox = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (nx + dx, ny + dy) in blocked:
                prox += 1
        if self_evader:
            # big weight on distance, medium on moving toward corner, small on staying away from obstacles
            return d2 * 10.0 + toward_corner * 0.05 - prox * 0.7 - man * 0.01 - align * 0.02
        else:
            # big weight on distance, medium on alignment (lower align is better), small obstacle penalty
            return -d2 * 10.0 - man * 0.1 - (2 - align) * 0.3 - prox * 0.6 - dist2(nx, ny, cx, cy) * 0.002

    best = [0, 0]
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = score(nx, ny)
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return [int(best[0]), int(best[1])]