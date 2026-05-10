def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ex, ey = observation.get("opponent_position", (W - 1, H - 1))
    ex, ey = int(ex), int(ey)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    targets = []
    for k in ("resources", "unclaimed_cells"):
        for p in observation.get(k) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                    targets.append((x, y))
        if targets:
            break

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        if targets:
            t = min(targets, key=lambda p: man((nx, ny), p))
            td = man((nx, ny), t)
        else:
            td = 0
        od = man((nx, ny), (ex, ey))
        score = -td + 0.2 * od
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]