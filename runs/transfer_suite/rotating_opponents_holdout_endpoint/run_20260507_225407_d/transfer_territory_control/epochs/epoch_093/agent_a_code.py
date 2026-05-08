def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    ox = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    px, py = int(ox[0]), int(ox[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    targets = []
    for key in ("unclaimed_cells", "resources"):
        vals = observation.get(key) or []
        for p in vals:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    targets.append((x, y))
        if targets:
            break

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((nx, ny, dx, dy))
    if not cand:
        for dx, dy in [(0, 0), (0, 1), (1, 0), (-1, 0), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    def best_for_targets(tx, ty):
        d = abs(tx - sx) + abs(ty - sy)
        return d

    if targets:
        targets = sorted(set(targets))
        best = None
        for nx, ny, dx, dy in cand:
            dist = min(abs(tx - nx) + abs(ty - ny) for tx, ty in targets)
            key = (dist, abs(px - nx) + abs(py - ny), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    # Fallback: move toward opponent territory/position
    best = None
    for nx, ny, dx, dy in cand:
        key = (abs(px - nx) + abs(py - ny), nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [int(best[1]), int(best[2])]