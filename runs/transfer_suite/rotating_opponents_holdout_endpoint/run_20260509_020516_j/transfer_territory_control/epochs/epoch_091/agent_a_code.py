def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (W - 1, H - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    res = observation.get("resources") or []
    rcells = set()
    for p in res:
        if p and len(p) >= 2:
            rcells.add((int(p[0]), int(p[1])))

    if oppT:
        cx, cy = sum(x for x, y in oppT) / len(oppT), sum(y for x, y in oppT) / len(oppT)
    else:
        cx, cy = ox, oy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in rcells:
            score += 3
        if (nx, ny) in selfT:
            score += 2
        if (nx, ny) in oppT:
            score += 5  # counterclaim threat, but flipping can still swing territory
        score -= 0.25 * dist2((nx, ny), (ox, oy))  # prefer staying away from opponent
        score -= 0.05 * dist2((nx, ny), (cx, cy))  # avoid their cluster/pressure
        # slight bias to expand toward the farther corner from opponent
        score += 0.02 * dist2((nx, ny), (0 if ox > W // 2 else W - 1, 0 if oy > H // 2 else H - 1))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]