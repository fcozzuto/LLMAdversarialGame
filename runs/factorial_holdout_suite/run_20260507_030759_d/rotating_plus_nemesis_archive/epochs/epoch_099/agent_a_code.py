def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # deterministic fallback: move toward center while avoiding obstacles
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best_score = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                sc = dist(nx, ny, tx, ty)
                if sc < best_score or (sc == best_score and (dx, dy) < best_move):
                    best_score, best_move = sc, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        # Prefer resources where we are not behind; slight bias toward closer overall.
        val = (opd - myd) * 2 - myd
        if val > best_val:
            best_val = val
            best_target = (rx, ry)
        elif val == best_val:
            if best_target is None or (rx, ry) < best_target:
                best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            sc = dist(nx, ny, tx, ty)
            # If tied, prefer moves that also increase distance from opponent for denier matchup.
            if sc < best_score:
                best_score = sc
                best_move = (dx, dy)
            elif sc == best_score:
                if dist(nx, ny, ox, oy) > dist(sx + best_move[0], sy + best_move[1], ox, oy):
                    best_move = (dx, dy)
                elif dist(nx, ny, ox, oy) == dist(sx + best_move[0], sy + best_move[1], ox, oy) and (dx, dy) < best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]