def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())
    unclaimed_set = set(tuple(p) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx + dy

    frontier = []
    for (x, y) in self_terr:
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed_set:
                frontier.append((nx, ny))
    targets = frontier if frontier else [c for c in unclaimed_set if inb(c[0], c[1])]
    if not targets:
        return [0, 0]

    # Choose nearest target with deterministic tie-break
    best_t = None
    best_td = 10**9
    for tx, ty in targets:
        td = dist(sx, sy, tx, ty)
        if td < best_td or (td == best_td and (tx, ty) < best_t):
            best_td, best_t = td, (tx, ty)
    tx, ty = best_t

    def adj_to_opp(x, y):
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr:
                return True
        return False

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10000
        else:
            val = 0
            if (nx, ny) in opp_terr:
                val += 200 - 2 * dist(nx, ny, tx, ty)
            elif (nx, ny) in unclaimed_set:
                val += 80 - dist(nx, ny, tx, ty)
            elif (nx, ny) in self_terr:
                val += 10 - 2 * dist(nx, ny, tx, ty)
            else:
                val += 0 - dist(nx, ny, tx, ty)
            if adj_to_opp(nx, ny):
                val += 8
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]