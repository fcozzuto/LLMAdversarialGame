def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def md(a, b):
        dx = a - b
        if dx < 0:
            dx = -dx
        return dx

    def dist2(x, y, tx, ty):
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        return dx + dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            return [dx, dy]
        score = 0
        if (nx, ny) in resources:
            score += 1000
        if (nx, ny) in unclaimed:
            score += 400
        if (nx, ny) in opp_terr:
            score += 120
        if (nx, ny) in self_terr:
            score += 60
        # Prefer moving toward nearby unclaimed/resources, away from opponent
        best_d = 10**9
        for tx, ty in resources:
            d = dist2(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
        for tx, ty in unclaimed:
            d = dist2(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                if best_d == 0:
                    break
        if best_d == 10**9:
            best_d = dist2(nx, ny, (w - 1) // 2, (h - 1) // 2)
        opp_d = dist2(nx, ny, ox, oy)
        score += 25 * (-best_d) + 8 * opp_d
        candidates.append((score, -dx * 0 + 0, dx, dy, (nx, ny)))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return [candidates[0][2], candidates[0][3]]