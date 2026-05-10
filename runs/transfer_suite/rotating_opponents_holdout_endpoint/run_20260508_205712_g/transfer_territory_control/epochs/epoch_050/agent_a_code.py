def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for t in (observation.get("obstacles") or []):
        obstacles.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in (observation.get("opponent_territory") or []):
        oppT.add((int(t[0]), int(t[1])))

    unclaimed = set()
    for t in (observation.get("unclaimed_cells") or []):
        unclaimed.add((int(t[0]), int(t[1])))

    resources = []
    for t in (observation.get("resources") or []):
        try:
            resources.append((int(t[0]), int(t[1])))
        except:
            pass

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_target():
        best = None
        bestd = 10**9
        for ux, uy in unclaimed:
            d = abs(ux - sx) + abs(uy - sy)
            # bias toward filling near center and toward nearer moves
            score = d + 0.3 * (abs(ux - cx) + abs(uy - cy))
            if score < bestd or (score == bestd and (ux, uy) < best):
                bestd = score
                best = (ux, uy)
        if best is not None:
            return best
        if resources:
            # go to closest resource
            return min(resources, key=lambda r: (abs(r[0] - sx) + abs(r[1] - sy), r[0], r[1]))
        return (int(round(cx)), int(round(cy)))

    target = best_target()
    tx, ty = target[0], target[1]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in oppT:
            score += 2000
        elif (nx, ny) in unclaimed:
            score += 900
        else:
            score += 50

        # expansion pressure: prefer closer to the current target
        dist_t = abs(nx - tx) + abs(ny - ty)
        score += 400 - 35 * dist_t

        # center control
        score += 10 * (8 - int(abs(nx - cx) + abs(ny - cy)))

        # resources attraction if adjacent/nearby
        if resources:
            md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            score += 300 - 25 * md

        # small preference for diagonals only when they reduce target distance
        if dx != 0 and dy != 0:
            if dist_t <= abs(sx - tx) + abs(sy - ty):
                score += 10

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move