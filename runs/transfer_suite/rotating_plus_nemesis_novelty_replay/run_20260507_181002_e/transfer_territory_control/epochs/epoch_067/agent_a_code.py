def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    candidates = []
    has_targets = bool(unclaimed)
    targets = list(unclaimed) if has_targets else []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if has_targets:
            d_us = 10**9
            d_op = 10**9
            for tx, ty in targets:
                d_us = min(d_us, md(nx, ny, tx, ty))
                d_op = min(d_op, md(ox, oy, tx, ty))
            # Prefer closer-to-resource and resources where we're not much behind opponent
            score = 200 - d_us - max(0, d_op - d_us) * 8
        else:
            # No known targets: hold center and keep away from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score = -md(nx, ny, int(cx), int(cy)) * 3 + md(nx, ny, ox, oy)

        # Prefer staying legal and stable
        if dx == 0 and dy == 0:
            score -= 1

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], -abs(t[1]) - abs(t[2])), reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]