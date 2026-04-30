def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine keeps agent in place

        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            val = -cheb(nx, ny, tx, ty)
            if val > best_val:
                best_val, best_move = val, (dx, dy)
            continue

        best_target_val = -10**18
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer targets where we are closer than the opponent, then faster overall
            adv = opd - myd
            val = adv * 10 - myd
            if (tx, ty) == (nx, ny):
                val += 10000
            if val > best_target_val:
                best_target_val = val

        # Mild preference to reduce opponent's ability: slightly maximize distance after move
        opp_escape = cheb(nx, ny, ox, oy)
        total = best_target_val + 0.02 * opp_escape
        if total > best_val:
            best_val, best_move = total, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]