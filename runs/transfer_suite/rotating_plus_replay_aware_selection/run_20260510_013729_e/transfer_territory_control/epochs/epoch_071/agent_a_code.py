def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    targets = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            targets.append((int(p[0]), int(p[1])))

    if not targets:
        op = observation.get("opponent_position") or [x, y]
        ox, oy = int(op[0]), int(op[1])
        targets = [(ox, oy)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = 10**18
    ox, oy = (int(observation.get("opponent_position")[0]), int(observation.get("opponent_position")[1])) if observation.get("opponent_position") else (x, y)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = min(dist((nx, ny), t) for t in targets) if targets else 0
        d_opp = dist((nx, ny), (ox, oy))
        cell_bonus = 0
        if observation.get("self_territory") and (nx, ny) in set(map(tuple, observation["self_territory"])):
            cell_bonus -= 1
        score = d_self - 0.05 * d_opp + cell_bonus
        if score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]