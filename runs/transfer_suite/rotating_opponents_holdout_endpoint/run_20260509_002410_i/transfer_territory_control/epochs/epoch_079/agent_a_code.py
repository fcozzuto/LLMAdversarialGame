def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda r: (abs(r[0] - sx) + abs(r[1] - sy), r[0], r[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = abs(nx - tx) + abs(ny - ty)
            tieb = (score, abs(dx), abs(dy), dx, dy, nx, ny)
            if best is None or tieb < best[0]:
                best = (tieb, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]