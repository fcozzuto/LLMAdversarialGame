def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    targets.append((x, y))
            except:
                pass

    if not targets:
        targets = [(w // 2, h // 2)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    center = (w // 2, h // 2)
    oppd = dist2((sx, sy), (ox, oy))

    best = (None, -10**18)
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d_to_target = min(dist2((nx, ny), t) for t in targets)
        d_away = dist2((nx, ny), (ox, oy))
        bias = 0
        if targets and (nx, ny) == center:
            bias += 1
        score = (-d_to_target) + (2.0 * d_away) + (0.01 * oppd) + bias
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]