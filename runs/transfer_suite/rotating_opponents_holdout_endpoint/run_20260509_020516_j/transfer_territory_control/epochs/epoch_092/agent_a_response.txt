def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
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

    opp_cells = []
    if oppT:
        for x, y in oppT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        opp_cells.append((nx, ny))
    if not opp_cells:
        for x, y in unclaimed:
            if (x, y) not in obstacles:
                opp_cells.append((x, y))

    rcells = observation.get("resources") or []
    # deterministic priority: nearest resource, else nearest frontier/unclaimed
    targets = []
    if rcells:
        for p in rcells:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                    targets.append((x, y))
    if not targets:
        opp_cells = sorted(set(opp_cells))
        targets = opp_cells[:10]

    def cheb(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_score = -10**9
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        score = 0.0
        if (nx, ny) in oppT:
            score += 4.5
        elif (nx, ny) in unclaimed:
            score += 2.5
        elif (nx, ny) in selfT:
            score += 0.5

        if targets:
            d0 = min(cheb((sx, sy), t) for t in targets)
            d1 = min(cheb((nx, ny), t) for t in targets)
            score += 0.05 * (d0 - d1)  # move toward target
        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best if best is not None else [0, 0]