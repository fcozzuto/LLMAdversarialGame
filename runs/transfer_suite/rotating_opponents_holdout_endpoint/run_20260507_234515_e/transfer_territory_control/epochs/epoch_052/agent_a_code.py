def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))
    opp = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp[0]), int(opp[1])

    if unclaimed:
        targets = sorted(unclaimed)
    elif resources:
        targets = sorted(resources)
    else:
        targets = [(ox, oy)]

    best_t = targets[0]
    best_d = abs(best_t[0] - sx) + abs(best_t[1] - sy)
    for tx, ty in targets[1:]:
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_d:
            best_d, best_t = d, (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        score = (d, abs(ox - nx) + abs(oy - ny), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]