def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escap" in role) or ("run" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x, y, a, b):
        return abs(x - a) + abs(y - b)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def free_count(x, y):
        c = 0
        for dx, dy in deltas:
            tx, ty = x + dx, y + dy
            if legal(tx, ty):
                c += 1
        return c

    if is_evader:
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = manh(nx, ny, ox, oy)
            # Avoid moving adjacent if possible (helps if pursuer is direct)
            adj = max(abs(nx - ox), abs(ny - oy)) == 1
            key = (d, -int(adj), free_count(nx, ny))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # Pursuer: move to capture if possible; else minimize distance, avoid "bad" retreats
    best = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = manh(nx, ny, ox, oy)
        cap = int((nx == ox) and (ny == oy))
        # Prefer moves that keep good mobility while closing distance
        key = (cap, -d, free_count(nx, ny))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]