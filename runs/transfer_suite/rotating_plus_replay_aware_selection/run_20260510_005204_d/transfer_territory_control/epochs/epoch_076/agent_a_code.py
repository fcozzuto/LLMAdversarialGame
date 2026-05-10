def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                self_terr.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))

    best_target = None
    if resources:
        best_target = min(resources, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        adj_unclaimed = []
        if self_terr:
            for x, y in unclaimed:
                if any((x + dx, y + dy) in self_terr for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    adj_unclaimed.append((x, y))
        cand = adj_unclaimed if adj_unclaimed else unclaimed
        if cand:
            best_target = min(cand, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        else:
            best_target = (w // 2, h // 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    tx, ty = best_target
    best = (0, 0)
    best_score = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        score = dist * 10
        if (nx, ny) in self_terr:
            score -= 1
        if (nx, ny) == (ox, oy):
            score += 20
        if score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]