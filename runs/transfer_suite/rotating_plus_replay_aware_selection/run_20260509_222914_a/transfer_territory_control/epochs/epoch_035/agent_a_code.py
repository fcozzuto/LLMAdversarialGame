def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    opp = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                opp.add((x, y))

    selft = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                selft.add((x, y))

    unclaimed = []
    for key in ("unclaimed_cells", "unclaimed"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y) and (x, y) not in obstacles:
                    unclaimed.append((x, y))
        if unclaimed:
            break

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if inside(nx, ny):
                        yield nx, ny

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for nx, ny in neigh8(sx, sy):
        if (nx, ny) in obstacles:
            continue
        candidates.append((nx, ny))

    if not candidates:
        return [0, 0]

    def cell_priority(x, y):
        # Prefer immediate counterclaim: move into opponent-adjacent unclaimed or opponent cell.
        adj_opp = 0
        for ax, ay in neigh8(x, y):
            if (ax, ay) in opp:
                adj_opp += 1
        in_opp = 1 if (x, y) in opp else 0
        is_unclaimed = 1 if ((x, y) in unclaimed) else 0
        # Keep progressing: bias toward center and away from staying in place.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(x - cx) + abs(y - cy)
        dist_to_opp = abs(x - ox) + abs(y - oy)
        # Large weights to deterministically focus on flipping/counterclaim.
        return (200 * in_opp + 40 * adj_opp + 10 * is_unclaimed - 0.5 * dist_to_opp - 0.01 * dist_center)

    best = None
    bestv = None
    for x, y in candidates:
        v = cell_priority(x, y)
        if best is None or v > bestv or (v == bestv and (x, y) < best):
            best = (x, y)
            bestv = v

    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]