def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Prefer expansion: unclaimed cells adjacent to our territory
    adj_unclaimed = set()
    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for ax, ay in self_ter:
        for dx, dy in neigh:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                adj_unclaimed.add((nx, ny))

    targets = adj_unclaimed if adj_unclaimed else (unclaimed if unclaimed else set())
    if not targets:
        # No unclaimed: reclaim nearest opponent territory cell
        targets = opp_ter if opp_ter else {(ox, oy)}

    def best_target_score(tx, ty):
        return abs(tx - sx) + abs(ty - sy)

    # Choose deterministic "best" target: minimal manhattan, tie by x then y
    target = None
    best_td = 10**9
    for tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_td or (d == best_td and (tx < target[0] or (tx == target[0] and ty < target[1]))):
            best_td = d
            target = (tx, ty)

    tx, ty = target

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0
        if (nx, ny) in unclaimed:
            val += 12
        elif (nx, ny) in opp_ter:
            val += 9
        elif (nx, ny) in self_ter:
            val += 3
        # Move toward target, but also avoid giving opponent a direct chase lane
        val += - (abs(nx - tx) + abs(ny - ty))
        val += - (abs(nx - ox) + abs(ny - oy)) * 0.02  # small bias away from opponent
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]