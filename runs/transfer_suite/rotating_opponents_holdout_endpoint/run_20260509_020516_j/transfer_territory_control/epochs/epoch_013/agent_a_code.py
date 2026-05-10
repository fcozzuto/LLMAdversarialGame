def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    def xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            if "x" in v and "y" in v:
                return int(v["x"]), int(v["y"])
        return 0, 0

    sx, sy = xy(observation.get("self_position", (0, 0)))
    ox, oy = xy(observation.get("opponent_position", (0, 0)))

    obs = set()
    for c in (observation.get("obstacles") or []):
        x, y = xy(c)
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best = (10**18, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        dist = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if (dx == 0 and dy == 0) or dist < best[0] or (dist == best[0] and dx == 0 and dy == 0):
            if dist < best[0]:
                best = (dist, (dx, dy))
            elif dist == best[0] and (dx, dy) < best[1]:
                best = (dist, (dx, dy))

    if best[1] is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]