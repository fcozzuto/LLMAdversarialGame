def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    ox, oy = (observation.get("opponent_position") or [w - 1, h - 1])[:2]

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # Build frontier targets from unclaimed near our territory; fallback to edge unclaimed then any unclaimed
    frontier = []
    if st and unclaimed:
        for x, y in st:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in unclaimed:
                        frontier.append((nx, ny))
    edge_unclaimed = [p for p in unclaimed if p[0] in (0, w - 1) or p[1] in (0, h - 1)]
    target_list = frontier or edge_unclaimed or list(unclaimed) or [(int(ox), int(oy))]
    # Deterministic target: minimize distance from us but prefer cells closer to center and farther from opponent
    target_list = sorted(set(target_list))
    def tscore(p):
        tx, ty = p
        return (man(sx, sy, tx, ty), -man(ox, oy, tx, ty), abs(tx - cx) + abs(ty - cy))
    tx, ty = target_list[0] if target_list else (ox, oy)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = sorted(moves, key=lambda d: (d[0], d[1]))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)
        gain = 0
        if pos in unclaimed:
            gain += 12
        if pos in ot:
            gain += 7
        if pos in st:
            gain += 3
        # Prefer moving toward target and away from opponent
        score = gain + (man(ox, oy, nx, ny) - man(ox, oy, sx, sy)) * 0.5 - man(nx, ny, tx, ty)
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]