def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    opp_terr = observation.get("opponent_territory") or []
    self_terr = observation.get("self_territory") or []
    opp_set = set(map(tuple, opp_terr))
    self_set = set(map(tuple, self_terr))
    un_set = set(map(tuple, unclaimed))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    if unclaimed:
        candidates = unclaimed
    elif resources:
        candidates = resources
    elif opp_terr:
        candidates = opp_terr
    else:
        candidates = [(w - 1, h - 1)]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Prefer unclaimed adjacent to our territory (expansion), else nearest candidate.
    expand_targets = []
    for x, y in candidates:
        if (x, y) in un_set:
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if (nx, ny) in self_set:
                    expand_targets.append((x, y))
                    break
    targets = expand_targets if expand_targets else candidates
    tx, ty = targets[0][0], targets[0][1]
    bestd = dist(sx, sy, tx, ty)
    for x, y in targets:
        d = dist(sx, sy, x, y)
        if d < bestd or (d == bestd and (y < ty or (y == ty and x < tx))):
            bestd, tx, ty = d, x, y

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        gain = 0
        if cell in self_set:
            gain += 0.5
        elif cell in un_set:
            gain += 2.0
        elif cell in opp_set:
            gain += 3.0
        # Extra push toward expansion target and toward the opponent when close.
        gain += 1.0 / (1.0 + dist(nx, ny, tx, ty))
        if opp_set:
            ox, oy = observation.get("opponent_position", [w - 1, h - 1])
            gain += 0.15 / (1.0 + dist(nx, ny, ox, oy))
        # Deterministic tie-break: prefer staying on-grid with lower dx,dy lexical.
        score = gain * 1000 - (abs(dx) + abs(dy))
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]