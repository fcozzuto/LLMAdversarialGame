def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax + ay

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        dx = 0
        dy = 0
        if sx < ox: dx = 1
        elif sx > ox: dx = -1
        if sy < oy: dy = 1
        elif sy > oy: dy = -1
        if (sx + dx, sy + dy) in obstacles:
            return [0, 0]
        return [dx, dy]

    resources.sort()
    best_t = resources[0]
    best_val = None
    for rx, ry in resources:
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer targets where we can arrive earlier; otherwise, choose closer overall but reduce opponent lead.
        val = (do - ds) * 100 - ds * 2
        if best_val is None or val > best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ns = manh(nx, ny, rx, ry)
        no = manh(ox, oy, rx, ry)
        # Move to decrease our distance; if equal, increase our advantage margin; then prefer staying closer to center line.
        score = (no - ns) * 100 - ns * 3
        if score < (best_score if best_score is not None else -10**18):
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: keep nearer diagonal-first order already in dirs; then smaller dx, then smaller dy.
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]