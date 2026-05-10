def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H:
            obs.add((x, y))

    targets = []
    for p in (observation.get("resources") or []):
        try:
            x, y = int(p[0]), int(p[1])
        except Exception:
            continue
        if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
            targets.append((x, y))

    if not targets:
        targets = [(W // 2, H // 2)]

    best_t = targets[0]
    best_d = None
    for x, y in targets:
        d = abs(x - sx) + abs(y - sy)
        if best_d is None or d < best_d:
            best_d, best_t = d, (x, y)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        d_t = abs(tx - nx) + abs(ty - ny)
        d_o = abs(ox - nx) + abs(oy - ny)
        score = (d_o * 2) - d_t
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]