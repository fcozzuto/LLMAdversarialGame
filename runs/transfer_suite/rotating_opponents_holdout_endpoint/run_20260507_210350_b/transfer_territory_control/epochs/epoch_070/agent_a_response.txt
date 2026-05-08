def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))
    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))
    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        if (nx, ny) in oppT:
            score = 10**7 - dist(nx, ny, ox, oy) * 5
        elif (nx, ny) in unclaimed:
            score = 200000 - dist(nx, ny, ox, oy) * 3 - (abs(nx - cx) + abs(ny - cy)) * 0.5
        else:
            score = 0

        if (nx, ny) in selfT:
            score += 5000
        score -= dist(nx, ny, ox, oy) * 0.2
        score += (abs(nx - cx) + abs(ny - cy)) * 0.05  # slight outward spread

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]