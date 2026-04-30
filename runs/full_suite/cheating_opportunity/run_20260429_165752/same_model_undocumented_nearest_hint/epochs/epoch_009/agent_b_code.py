def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H -1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            md_me = 10**9
            md_op = 10**9
            for rx, ry in resources:
                d1 = abs(nx - rx) + abs(ny - ry)
                if d1 < md_me:
                    md_me = d1
                d2 = abs(ox - rx) + abs(oy - ry)
                if d2 < md_op:
                    md_op = d2
            key = (md_me, -(md_op - md_me), dx, dy, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
    else:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]