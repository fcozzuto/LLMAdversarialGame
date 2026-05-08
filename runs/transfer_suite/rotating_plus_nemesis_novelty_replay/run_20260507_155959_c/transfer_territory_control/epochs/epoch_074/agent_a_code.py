def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets:
        targets = [(ox, oy)]

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < md:
                md = d
        # tie-break: prefer moving closer, then closer to opponent, then earlier dir order
        key = (md, abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is not None:
        return [best[0], best[1]]
    return [0, 0]