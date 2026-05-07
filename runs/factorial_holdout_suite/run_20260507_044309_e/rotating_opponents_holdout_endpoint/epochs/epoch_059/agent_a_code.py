def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    def king_d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not resources:
        tx = ox - sx
        ty = oy - sy
        dx = 0 if tx == 0 else (1 if tx > 0 else -1)
        dy = 0 if ty == 0 else (1 if ty > 0 else -1)
        return [dx, dy]

    best_t = None
    best_val = None
    for t in resources:
        sd = king_d((sx, sy), t)
        od = king_d((ox, oy), t)
        val = (od - sd, -sd, -t[0], -t[1])  # prefer winning race, then closer, then deterministic
        if best_val is None or val > best_val:
            best_val = val
            best_t = t
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = king_d((nx, ny), (tx, ty))
        nod = king_d((ox, oy), (tx, ty))
        adv = nod - nsd
        mv = (adv, -nsd, -king_d((nx, ny), (ox, oy)), dx, dy)
        if best_mv is None or mv > best_mv:
            best_mv = mv
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]