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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        best_key = None
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer targets where we can arrive earlier; otherwise, reduce opponent's advantage.
            lead = od - sd
            key = (lead, -sd, tx, ty)  # lexicographic max
            if best_key is None or key > best_key:
                best_key = key
                best = (tx, ty)
        return best

    tx, ty = best_target()

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - nd
        # Break ties by moving closer, then keep direction toward target.
        to_tx = 0 if tx == nx else (1 if tx > nx else -1)
        to_ty = 0 if ty == ny else (1 if ty > ny else -1)
        dir_bonus = (dx == to_tx) + (dy == to_ty)
        key = (lead, -nd, dir_bonus, -abs(tx - nx) - abs(ty - ny))
        cand.append((key, [dx, dy]))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda z: z[0], reverse=True)
    return cand[0][1]