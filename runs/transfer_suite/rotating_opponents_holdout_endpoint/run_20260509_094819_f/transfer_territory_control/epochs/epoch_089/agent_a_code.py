def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    self_cells = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                self_cells.add((x, y))

    opp_cells = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                opp_cells.add((x, y))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def nearest_dist(cell):
        x, y = cell
        best = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < best:
                best = d
        return best if resources else 0

    best_move = (0, 0)
    best_score = -10**18
    target = (ox, oy)  # fallback

    if resources:
        target = min(resources, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
    elif unclaimed:
        target = min(unclaimed, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in self_cells:
            score += 5
        if (nx, ny) in opp_cells:
            score -= 30
        if (nx, ny) in unclaimed:
            score += 20
        if (nx, ny) in resources:
            score += 80
        tx, ty = target
        dist = abs(tx - nx) + abs(ty - ny)
        score += -dist
        if resources and not unclaimed:
            score += -nearest_dist((nx, ny)) // 2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]