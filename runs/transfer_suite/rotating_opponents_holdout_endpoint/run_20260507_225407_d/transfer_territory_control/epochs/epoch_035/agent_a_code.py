def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    targets = list(to_set("unclaimed_cells"))
    if not targets:
        targets = list(to_set("resources"))
    if not targets:
        targets = [(0, 0), (w - 1, h - 1), (sx, sy)]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # distance to closest target
        dmin = None
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if dmin is None or d < dmin:
                dmin = d
        # keep away from opponent
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = (1000 - (dmin if dmin is not None else 10**9)) + d_opp
        key = (-score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    if best is not None:
        return best[1]

    # fallback: deterministic attempt to avoid obstacles, else stay
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]