def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if w is not None else 8
    h = int(h) if h is not None else 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            candidates.append((False, dx, dy, nx, ny))
        else:
            candidates.append((True, dx, dy, nx, ny))

    safe = [c for c in candidates if c[0]]
    use = safe if safe else candidates
    best = None
    for ok, dx, dy, nx, ny in use:
        d = dist2(nx, ny)
        val = d if is_evader else -d
        if (best is None) or (val > best[0]) or (val == best[0] and (dx, dy) < (best[1], best[2])):
            best = (val, dx, dy)
    return [best[1], best[2]]