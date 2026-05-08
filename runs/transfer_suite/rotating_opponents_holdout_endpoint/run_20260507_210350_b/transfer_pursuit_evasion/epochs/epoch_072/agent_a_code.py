def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    pursuer_mode = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Deterministic target choice to change behavior each turn (avoid repeating a single line)
    phase = (int(observation.get("turn_index", 0)) % 6)
    base_corner = corners[phase % 4]
    if pursuer_mode:
        # In pursuit, bias toward corner that forces a clearer line away from opponent
        target_corner = max(corners, key=lambda c: -cheb(c[0], c[1], ox, oy))
    else:
        # In evasion, head to farthest corner from opponent, with periodic alternation
        target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        if cheb(base_corner[0], base_corner[1], ox, oy) == cheb(target_corner[0], target_corner[1], ox, oy):
            target_corner = base_corner

    tx, ty = target_corner
    # Score candidates: maximize distance if evader, minimize if pursuer. Strongly discourage stepping into obstacles.
    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        corner_push = -cheb(nx, ny, tx, ty)  # closer to chosen target is good
        # Additional wall/obstacle penalty: avoid being too close to obstacles where opponent can trap.
        adj = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                axx, ayy = nx + adx, ny + ady
                if inb(axx, ayy) and blocked(axx, ayy):
                    adj += 1
        s = d
        if pursuer_mode:
            s = -d + 0.25 * corner_push - 0.15 * adj
        else:
            s = d + 0.25 * corner_push - 0.35 * adj
        if best is None or (s > best_s if not pursuer_mode else s > best_s):
            best_s = s
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]