def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    targets = []
    resources = observation.get("resources", []) or []
    if isinstance(resources, list) and resources:
        for p in resources:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((int(p[0]), int(p[1])))
    if not targets:
        unclaimed = observation.get("unclaimed_cells", []) or []
        if isinstance(unclaimed, list) and unclaimed:
            for p in unclaimed:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    targets.append((int(p[0]), int(p[1])))
    if not targets:
        targets = [(ox, oy)]

    cand = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        best_t = min(dist2(nx, ny, tx, ty) for tx, ty in targets)
        score = best_t
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort()
    return [int(cand[0][1]), int(cand[0][2])]