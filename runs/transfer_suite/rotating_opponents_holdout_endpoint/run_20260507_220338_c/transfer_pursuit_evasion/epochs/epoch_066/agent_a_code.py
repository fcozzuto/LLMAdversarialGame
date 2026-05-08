def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Wall-avoid: discourage moves into/near dense obstacle pockets.
    def obs_density(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in blocked:
                    c += 1
        return c

    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d = cheb(nx, ny, ox, oy)
        dens = obs_density(nx, ny)
        # small deterministic preference to reduce staying: favor non-zero moves slightly
        step = 1 if (dx != 0 or dy != 0) else 0

        if is_evader:
            # maximize distance; also avoid dense obstacle areas and keep some mobility
            v = (d * 100) + (step * 2) - (dens * 3)
            # slight cornering: prefer moving toward farthest corner from pursuer
            cx1, cy1 = 0, 0
            cx2, cy2 = w - 1, h - 1
            far_corner = (cx1 if cheb(nx, ny, cx1, cy1) > cheb(nx, ny, cx2, cy2) else cx2,
                          cy1 if cheb(nx, ny, cx1, cy1) > cheb(nx, ny, cx2, cy2) else cy2)
            v += cheb(nx, ny, far_corner[0], far_corner[1])
        else:
            # minimize distance; also avoid obstacle pockets to prevent getting boxed in
            v = (-d * 100) + (step * 2) - (dens * 3)

        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best