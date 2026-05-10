def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = observation.get("unclaimed_cells") or None
    if targets:
        pts = [(int(p[0]), int(p[1])) for p in targets if p and len(p) >= 2 and inside(int(p[0]), int(p[1]))]
    else:
        pts = None

    if not pts:
        res = observation.get("resources") or None
        if res:
            pts = [(int(p[0]), int(p[1])) for p in res if p and len(p) >= 2 and inside(int(p[0]), int(p[1]))]
        else:
            pts = [(w // 2, h // 2)]

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in pts) if pts else abs(nx - ox) + abs(ny - oy)
        do = abs(nx - ox) + abs(ny - oy)
        key = (md, -do, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]