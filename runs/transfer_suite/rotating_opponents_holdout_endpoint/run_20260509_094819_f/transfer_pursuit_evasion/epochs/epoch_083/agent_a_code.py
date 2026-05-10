def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    # Target: one step past opponent away from grid center (a crude "cut off")
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    vx = ox - cx
    vy = oy - cy
    tx = ox + (1 if vx > 0 else -1 if vx < 0 else 0)
    ty = oy + (1 if vy > 0 else -1 if vy < 0 else 0)

    # Clamp target inside grid and avoid obstacles if possible
    tx = 0 if tx < 0 else (w - 1 if tx >= w else tx)
    ty = 0 if ty < 0 else (h - 1 if ty >= h else ty)
    if (tx, ty) in blocked:
        tx, ty = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        d_to_op = cheb(nx, ny, ox, oy)
        d_to_t = cheb(nx, ny, int(tx), int(ty))

        # Extra incentive: align closer to the opponent's direction relative to us
        adx = ox - nx
        ady = oy - ny
        mag = 1
        if adx < 0: adx = -adx
        if ady < 0: ady = -ady
        mag = adx + ady + 1

        # Primary: minimize distance to opponent; Secondary: minimize distance to target; Tertiary: avoid giving evasion room
        val = (d_to_op * 1000 + d_to_t * 3) + (mag * 0.01)
        if val < best[0]:
            best = (val, (dx, dy))

    if best[1] is None:
        # Fallback: stay
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]