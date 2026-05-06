def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick target resource: prefer ones we're closer to, but also slightly closer overall.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        val = (od - sd) * 20 - sd - (rx * 0.001 + ry * 0.001)
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        moves = [(0, 0, sx, sy)]

    # Evaluate: move to reduce our distance while keeping pressure on opponent (they should also be far).
    cx0, cy0 = (w - 1) * 0.5, (h - 1) * 0.5
    bestm = None
    for dx, dy, nx, ny in moves:
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        center = -((nx - cx0) * (nx - cx0) + (ny - cy0) * (ny - cy0)) * 1e-4
        # Also nudge toward getting onto the target early.
        val = (od - sd) * 10 - sd * 2 + center
        # Tie-break deterministically: prefer moves with smaller distance; then lexicographic.
        t = (val, -sd, abs(dx), abs(dy), dx, dy)
        if bestm is None or t > bestm[0]:
            bestm = (t, dx, dy)
    return [int(bestm[1]), int(bestm[2])]