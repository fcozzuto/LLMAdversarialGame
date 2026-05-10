def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    inside = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    nbrs8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def frontier_from(terr):
        f = set()
        for x, y in terr:
            for dx, dy in nbrs8:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in terr:
                    f.add((nx, ny))
        return f

    my_front = frontier_from(self_terr)
    opp_front = frontier_from(opp_terr)

    # Deterministic target selection
    targets = []
    for t in my_front:
        if t in unclaimed:
            targets.append((0, t[0], t[1]))
    if not targets:
        for t in my_front:
            if t in unclaimed or t in opp_terr:
                targets.append((1, t[0], t[1]))
    if not targets:
        for t in opp_front:
            if t in unclaimed or t in self_terr or t in opp_terr:
                targets.append((2, t[0], t[1]))
    if not targets:
        if unclaimed:
            t = min(unclaimed, key=lambda q: (abs(q[0] - sx) + abs(q[1] - sy), q[1], q[0]))
            targets = [(3, t[0], t[1])]
        elif opp_terr:
            t = min(opp_terr, key=lambda q: (abs(q[0] - sx) + abs(q[1] - sy), q[1], q[0]))
            targets = [(3, t[0], t[1])]
        else:
            return [0, 0]

    # Pick best target with deterministic tie-breaking
    best_key = None
    best_t = None
    for pri, tx, ty in targets:
        d = abs(tx - sx) + abs(ty - sy)
        key = (pri, d, ty, tx)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)
    tx, ty = best_t

    # Choose move that reduces distance; slight preference toward unclaimed, then opponent territory
    def cell_value(x, y):
        if (x, y) in unclaimed:
            return 2
        if (x, y) in opp_terr:
            return 1
        if (x, y) in my_front:
            return 0
        return -1

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dist = abs(tx - nx) + abs(ty - ny)
        score = (dist, -cell_value(nx, ny), abs(dx) + abs(dy), dy, dx)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]