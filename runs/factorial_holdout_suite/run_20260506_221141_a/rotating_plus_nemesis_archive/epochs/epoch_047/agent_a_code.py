def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = None

    # If no resources, move to keep distance and roughly toward center
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h): 
                continue
            if (nx, ny) in obstacles:
                continue
            dist_opp = cheb(nx, ny, ox, oy)
            center = cheb(nx, ny, cx, cy)
            val = -dist_opp + 0.15 * center
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Target selection: prefer resources where we are closer than opponent after this move
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Slight bias toward staying on the shortest diagonal/straight path by using next-pos distance only
        chosen = None
        chosen_adv = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Lower is better: capture quickly; also discourage targets opponent reaches sooner
            adv = ds - 1.2 * do + 0.05 * (abs(tx - ox) + abs(ty - oy))
            if chosen_adv is None or adv < chosen_adv:
                chosen_adv = adv
                chosen = (tx, ty)

        tx, ty = chosen
        ds_cur = cheb(sx, sy, tx, ty)
        ds_next = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)

        # Combine: progress plus advantage; also ensure we don't backtrack too much
        val = ds_next + 0.35 * max(0, ds_next - ds_cur) - 0.9 * max(0, do - ds_next)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]