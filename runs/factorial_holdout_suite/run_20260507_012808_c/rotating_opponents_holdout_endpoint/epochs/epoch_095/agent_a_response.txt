def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def xy(v):
        try:
            return (int(v[0]), int(v[1]))
        except:
            return (0, 0)

    sx, sy = xy(observation.get("self_position"))
    ox, oy = xy(observation.get("opponent_position"))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = xy(p)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = xy(r)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    mid = (w - 1) / 2.0
    prefer_ours = (sx <= mid)  # if we start on left half, prefer left resources; else right
    def in_our_half(x):
        return (x <= mid) if prefer_ours else (x >= mid)

    best = None
    best_key = None
    for t in resources:
        my_d = cheb((sx, sy), t)
        opp_d = cheb((ox, oy), t)
        # Prefer targets we can reach not later than opponent, and on our side to fight sweep patterns.
        side_pen = 3 if not in_our_half(t[0]) else 0
        key = (my_d - opp_d + side_pen, my_d, abs(t[0] - sx) + abs(t[1] - sy))
        if best_key is None or key < best_key:
            best_key = key
            best = t

    tx, ty = best
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = cheb((nx, ny), (tx, ty))
        # Slightly prefer moves that also reduce Manhattan to discourage dithering.
        man = abs(nx - tx) + abs(ny - ty)
        key = (val, man)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]