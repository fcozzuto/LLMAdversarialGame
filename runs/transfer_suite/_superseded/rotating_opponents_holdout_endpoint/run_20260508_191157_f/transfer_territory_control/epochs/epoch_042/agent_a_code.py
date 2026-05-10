def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    targets = list(unclaimed) if unclaimed else (resources if resources else [(ox, oy)])

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (-10**18, 10**9, 0, 0)
    center = ((w - 1) // 2, (h - 1) // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        cell = (nx, ny)

        score = 0
        if cell in self_t:
            score += 1
        if cell in opp_t:
            score -= 6
        if cell in unclaimed:
            score += 10
        if cell == (ox, oy):
            score += 2

        d_to_target = min(md(cell, t) for t in targets) if targets else 0
        d_to_center = md(cell, center)
        score += 20 - d_to_target
        score -= d_to_center // 3

        dist_from_current = md(cell, (sx, sy))
        if (score, -dist_from_current, -d_to_target, dx, dy) > (best[0], -best[1], -best[2], best[2], best[3]):
            best = (score, d_to_target, dx, dy)

    return [best[2], best[3]]