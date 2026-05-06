def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_target = min(resources, key=lambda c: manh((ox, oy), c))
    opp_d = manh((ox, oy), opp_target)

    if opp_d <= 2:
        target = max(resources, key=lambda c: (manh((ox, oy), c), -manh((sx, sy), c)))
    else:
        target = max(resources, key=lambda c: (manh((ox, oy), c) - manh((sx, sy), c), -manh((sx, sy), c), manh((ox, oy), c)))

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy)]
    for m in cand:
        nx, ny = sx + m[0], sy + m[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(m[0]), int(m[1])]

    return [0, 0]