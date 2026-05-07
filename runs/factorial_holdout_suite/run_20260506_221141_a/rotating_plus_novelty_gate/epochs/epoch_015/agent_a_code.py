def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = [[False] * w for _ in range(h)]
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs[y][x] = True

    if not resources:
        return [0, 0]

    # Greedy: go to nearest resource (Manhattan), pick deterministic tie by (y,x)
    best = None
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < w and 0 <= y < h):
            continue
        if obs[y][x]:
            continue
        d = abs(x - sx) + abs(y - sy)
        key = (d, y, x)
        if best is None or key < best[0]:
            best = (key, x, y)
    if best is None:
        return [0, 0]

    _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen = set()
    for mx, my in moves:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and not obs[ny][nx]:
            # Prefer moves that reduce distance to target; otherwise take first safe deterministic
            if mx == dx or my == dy or (abs(tx - nx) + abs(ty - ny) <= abs(tx - sx) + abs(ty - sy)):
                return [int(mx), int(my)]

    # Fallback: any safe move
    for my in (-1, 0, 1):
        for mx in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and not obs[ny][nx]:
                return [int(mx), int(my)]
    return [0, 0]