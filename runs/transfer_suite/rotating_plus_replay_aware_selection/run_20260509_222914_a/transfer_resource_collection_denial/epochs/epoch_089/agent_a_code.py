def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manhattan(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose best target deterministically: maximize (opp_dist - self_dist), then closer self, then lexicographic
    best_target = None
    best_key = None
    for (rx, ry) in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # larger key better with deterministic ordering via comparisons below
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target

    # From each possible move, prefer one that reduces distance to chosen target and improves lead vs opponent
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sd2 = manhattan(nx, ny, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        lead = od - sd2
        # primary: maximize lead; secondary: minimize self distance; tertiary: prefer lexicographically smaller move delta for determinism
        score = (lead, -sd2, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if (best_move[0] in (-1, 0, 1) and best_move[1] in (-1, 0, 1)) else [0, 0]