def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Anti-sweep: if opponent is moving along rows, capture a resource on/near our row first.
    same_row = [r for r in resources if r[1] in (sy, sy + 1, sy - 1)]
    candidates = same_row if same_row else resources

    best = None
    best_key = None
    for rx, ry in candidates:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer immediate/near capture with advantage over opponent.
        # Key: higher advantage, then closer, then stable deterministic tie-break by coordinates.
        adv = od - sd
        key = (adv, -sd, -abs(rx - sx) - abs(ry - sy), -(rx * 97 + ry * 53))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    dy = 0
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked or not (0 <= nx < w and 0 <= ny < h):
        # Fallback: try axis-aligned deterministic steps toward target.
        options = []
        if dx != 0:
            options.append((sx + dx, sy))
        if dy != 0:
            options.append((sx, sy + dy))
        options.append((sx, sy))
        for tx, ty in options:
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in blocked:
                return [tx - sx, ty - sy]
        return [0, 0]

    return [dx, dy]