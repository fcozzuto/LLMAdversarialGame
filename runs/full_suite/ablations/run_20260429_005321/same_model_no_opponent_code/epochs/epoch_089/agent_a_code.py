def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    if resources:
        tx, ty = min(resources, key=lambda r: dist(sx, sy, r[0], r[1]))
        best = None
        best_sc = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            dres = dist(nx, ny, tx, ty)
            dop = dist(nx, ny, ox, oy)
            sc = dres * 10 - min(dop, 50)  # prioritize resource; avoid opponent a bit
            if best_sc is None or sc < best_sc or (sc == best_sc and (dx, dy) < best):
                best_sc = sc
                best = (dx, dy)
        if best is not None:
            return [int(best[0]), int(best[1])]

    # No reachable resource or all blocked: move to increase distance from opponent
    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        dop = dist(nx, ny, ox, oy)
        sc = -dop  # maximize distance => minimize -distance
        if best_sc is None or sc < best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        # Last resort: stay put if allowed by validator; otherwise choose a safe in-bounds move deterministically
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best[0]), int(best[1])]