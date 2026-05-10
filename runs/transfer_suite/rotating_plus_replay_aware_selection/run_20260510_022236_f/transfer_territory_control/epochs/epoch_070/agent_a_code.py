def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    neigh = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def is_blocked(x, y): return (x, y) in obstacles

    frontier = set()
    for x, y in self_terr:
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in self_terr:
                frontier.add((nx, ny))

    targets = []
    # Prefer conquering frontier (unclaimed first), else any nearby cell from opponent/unclaimed
    for cell in frontier:
        if cell in unclaimed or cell in op_terr:
            targets.append(cell)
    if not targets:
        for cell in unclaimed:
            targets.append(cell)
            if len(targets) >= 20: break
        if not targets:
            for cell in op_terr:
                targets.append(cell)
                if len(targets) >= 20: break

    best = None
    for tx, ty in targets:
        if not inb(tx, ty) or is_blocked(tx, ty):
            continue
        d = abs(tx - sx) + abs(ty - sy)
        frontier_bonus = -1 if (tx, ty) in frontier else 0  # smaller is better
        # Prefer unclaimed over opponent-owned (flip also good, but unclaimed often safer)
        owner_pen = 1 if (tx, ty) in op_terr else 0
        key = (frontier_bonus, d, owner_pen, ty, tx)
        if best is None or key < best[0]:
            best = (key, (tx, ty))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    cand_steps = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not is_blocked(nx, ny):
            # Choose step minimizing manhattan distance to target, tie-break deterministically
            cand_steps.append((abs(tx - nx) + abs(ty - ny), dx, dy, nx, ny))
    if not cand_steps:
        return [0, 0]

    cand_steps.sort()
    return [int(cand_steps[0][1]), int(cand_steps[0][2])]