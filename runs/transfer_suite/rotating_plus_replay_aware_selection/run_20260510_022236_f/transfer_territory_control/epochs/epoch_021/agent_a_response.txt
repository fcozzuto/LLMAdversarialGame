def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer cells adjacent to our territory (faster secure + less risk), else any unclaimed.
    candidates = []
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    for p in unclaimed:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue
        if self_terr:
            adj = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (tx + dx, ty + dy) in self_terr:
                    adj = True
                    break
            if not adj:
                continue
        candidates.append((tx, ty))

    if not candidates:
        candidates = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]

    best = None
    best_key = None
    for tx, ty in candidates:
        if (tx, ty) in obstacles or not (0 <= tx < w and 0 <= ty < h):
            continue
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # Centrality bias for longer-term control; discourage giving opponent too-close targets.
        center = abs(tx - cx0) + abs(ty - cy0)
        # Rank: primarily nearest to us, then farther from opponent, then closer to center.
        key = (ds, -(do), center)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy: minimize distance to target; tie-break by preferring moving away from opponent.
        dnt = man(nx, ny, tx, ty)
        dne = man(nx, ny, ox, oy)
        key = (dnt, -dne)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]