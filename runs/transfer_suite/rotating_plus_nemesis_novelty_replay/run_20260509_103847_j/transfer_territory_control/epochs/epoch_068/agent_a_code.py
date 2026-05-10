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

    targets = []
    for key in ("unclaimed_cells", "opponent_territory", "resources"):
        vals = observation.get(key) or []
        if vals:
            for p in vals:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                        targets.append((x, y))
                if len(targets) >= 30:
                    break
            if targets:
                break

    if not targets:
        return [0, 0]

    def manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_t = targets[0]
    best_d = manh((sx, sy), best_t)
    for t in targets[1:]:
        d = manh((sx, sy), t)
        if d < best_d:
            best_d, best_t = d, t

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = manh((nx, ny), best_t)
        d_o = manh((nx, ny), (ox, oy))
        score = (-d_t) + (0.3 * d_o)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]