def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid_moves.append((dx, dy))

    # Choose resource with best "capture advantage" (opponent farther than us).
    best_t = resources[0]
    best_val = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Encourage close targets, and winning contests; slight preference for lower coordinates for determinism.
        val = (od - sd) * 10 - sd + (-0.001 * (rx * 8 + ry))
        if best_val is None or val > best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    # Move toward target; if multiple, pick deterministically minimizing distance, then prefer progress.
    best_move = (0, 0)
    best_md = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        md = man(nx, ny, rx, ry)
        # progress toward target vs away from opponent (tiny deterrent for walking into opponent's lane)
        pd = (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))
        key = (md, -pd, dx, dy)
        if best_md is None or key < best_md:
            best_md = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]