def choose_move(observation):
    W = int(observation.get("grid_width") or 0)
    H = int(observation.get("grid_height") or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v, d=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict) and "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        return d

    sx, sy = xy(observation.get("self_position", (0, 0)))
    ox, oy = xy(observation.get("opponent_position", (0, 0)))

    obstacles = set()
    for c in (observation.get("obstacles") or []):
        x, y = xy(c, None) if isinstance(c, dict) else xy(c, None)
        if x is None:
            continue
        if 0 <= x < W and 0 <= y < H:
            obstacles.add((x, y))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    bx = -10**18
    for dx, dy, nx, ny in moves:
        r = 0
        if (nx, ny) in unclaimed:
            r += 6
        if (nx, ny) in self_t:
            r += 2
        if (nx, ny) in opp_t:
            r -= 6
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        r -= dist_to_opp * 0.1
        dist_to_center = abs(nx - (W - 1) / 2) + abs(ny - (H - 1) / 2)
        r -= dist_to_center * 0.01
        t = r
        if best is None or t > bx:
            bx = t
            best = (dx, dy)
        elif t == bx:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]