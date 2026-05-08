def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w, h = int(w), int(h)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                targets.append((x, y))

    if not targets:
        cx, cy = w // 2, h // 2
        targets = [(cx, cy)]

    dirs = [(0, -1), (-1, 0), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bx = by = 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocks:
            continue
        # Prefer closer to nearest resource; also slightly avoid opponent
        md = 10**9
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d < md:
                md = d
        od = abs(nx - ox) + abs(ny - oy)
        score = -md - 0.01 * od
        if best is None or score > best:
            best = score
            bx, by = dx, dy

    if best is None:
        # No legal move: try staying if not blocked, else any in-bounds non-blocked
        if (sx, sy) not in blocks:
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks:
                return [dx, dy]
        return [0, 0]

    return [bx, by]