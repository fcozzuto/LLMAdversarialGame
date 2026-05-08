def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_step(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources where we are not slower; otherwise pick least-losing.
        best = None
        best_key = None
        best_fast = None
        best_fast_key = None
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            key = (dO - dS, -dS, (rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2)
            if dS <= dO:
                if best_fast is None or key > best_fast_key:
                    best_fast, best_fast_key = (rx, ry), key
            if best is None or key > best_key:
                best, best_key = (rx, ry), key
        tx, ty = best_fast if best_fast is not None else best

    dx = clamp_step(tx - sx)
    dy = clamp_step(ty - sy)
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy), (0, 0)]

    def is_block(nx, ny):
        return (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h)

    best_move = [0, 0]
    best_val = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if is_block(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Also reduce chance of opponent taking it by moving toward it faster than them when possible.
        opp_d = cheb(ox, oy, tx, ty)
        val = (opp_d - d, -d, -cheb(nx, ny, ox, oy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [mx, my]

    return best_move