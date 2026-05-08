def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    target_corner = None
    best_corner_d2 = -1
    for cx, cy in corners:
        d2 = dist2(cx, cy, ox, oy)
        if d2 > best_corner_d2:
            best_corner_d2 = d2
            target_corner = (cx, cy)

    best_score = None
    best_move = [0, 0]
    for dx, dy in sorted(dirs):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # small obstacle penalty/bonus for local "escape lanes"
        block_adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obst:
                    block_adj += 1

        if evader:
            cx, cy = target_corner
            toward_corner = -dist2(nx, ny, cx, cy)  # closer to chosen corner is better
            score = d_opp * 10 + toward_corner - block_adj
        else:
            toward_opponent = -d_opp * 10  # minimize distance to capture faster
            # slight preference to approach while reducing freedom of opponent
            center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
            score = toward_opponent + center_bias - block_adj * 0.2

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move