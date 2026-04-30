def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py): obstacles.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    # Heuristic priority: grab nearest resource considering opponent, then avoid getting too close to opponent
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # distance to nearest resource after move
        if resources:
            d = min(dist((nx, ny), r) for r in resources)
        else:
            d = 0
        # distance to opponent (prefer not to collide, but can approach if beneficial)
        opd = dist((nx, ny), (ox, oy))
        # Center bias
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = dist((nx, ny), (cx, cy))
        # composite score: want closer to resource, not too close to opponent, modest center bias
        score = 0
        if resources:
            score += max(0, 10 - d * 2)
        # discourage being adjacent to opponent
        if max(abs(nx - ox), abs(ny - oy)) <= 1:
            score -= 5
        score -= center_dist * 0.5
        score -= opd * 0.1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move