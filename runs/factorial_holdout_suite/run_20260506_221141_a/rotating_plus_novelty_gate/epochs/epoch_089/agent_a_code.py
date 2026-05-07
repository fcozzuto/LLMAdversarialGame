def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(z):
        return 1 if z > 0 else (-1 if z < 0 else 0)

    res_sorted = sorted(resources)
    best = None
    best_adv = -10**18
    best_sd = 10**9
    for rx, ry in res_sorted:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        adv = od - sd
        if (adv > best_adv) or (adv == best_adv and (sd < best_sd or (sd == best_sd and (best is None or (rx, ry) < best)))):
            best_adv = adv
            best_sd = sd
            best = (rx, ry)

    tx, ty = best
    primary_dx = sign(tx - sx)
    primary_dy = sign(ty - sy)
    candidates = []
    # Prefer diagonal/axis step toward target; deterministic tie-order
    for dx in (primary_dx,):
        for dy in (primary_dy,):
            candidates.append((dx, dy))
    # Additional deterministic alternatives if blocked or ineffective
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        if (dx, dy) not in candidates:
            candidates.append((dx, dy))

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        # Evaluate landing by expected advantage after move
        sd2 = kdist(nx, ny, tx, ty)
        od2 = kdist(ox, oy, tx, ty)
        # Keep moving towards target; also avoid giving opponent a closer race by maximizing (od2 - sd2)
        val = (od2 - sd2) * 100 - sd2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]