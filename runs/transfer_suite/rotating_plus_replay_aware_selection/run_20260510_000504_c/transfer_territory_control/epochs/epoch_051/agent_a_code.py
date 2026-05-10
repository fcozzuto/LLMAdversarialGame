def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    resources = observation.get("resources") or []
    self_terr = set(map(tuple, observation.get("self_territory") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_moves = []
    target = None

    frontier = []
    for (x, y) in unclaimed:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in self_terr:
                    frontier.append((x, y))
                    dx = dy = None
                    break
            if dx is None:
                break
    if frontier:
        target = min(frontier, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    else:
        if resources:
            try:
                target = min([tuple(r) for r in resources], key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
            except Exception:
                target = None
        if target is None:
            target = (px, py)

    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) == target:
            score += 10_000
        if (nx, ny) in unclaimed:
            score += 400
        if (nx, ny) in self_terr:
            score += 20
        score += - (abs(nx - target[0]) + abs(ny - target[1]))
        score += - (abs(nx - px) + abs(ny - py)) * 0.05
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_moves[0]):
            best_score = score
            best_moves = [(dx, dy)]

    return [int(best_moves[0][0]), int(best_moves[0][1])]