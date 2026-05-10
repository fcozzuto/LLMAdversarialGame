def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if x is None or y is None:
                continue
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    path = observation.get("self_path") or []
    recent = set()
    for p in path[-8:]:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            recent.add((int(p[0]), int(p[1])))

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox) + abs(ny - oy)
        v = -d
        if (nx, ny) in recent:
            v -= 5
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v -= 0.01 * (abs(nx - cx) + abs(ny - cy))
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best