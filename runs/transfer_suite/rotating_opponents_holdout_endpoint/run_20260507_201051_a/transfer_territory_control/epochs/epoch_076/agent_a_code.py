def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    myT = set()
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            myT.add((int(p[0]), int(p[1])))
    enT = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            enT.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs8 = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    def adj_to_enemy(x, y):
        for dx, dy in dirs8:
            if (x + dx, y + dy) in enT:
                return True
        return False

    # Prefer unclaimed cells adjacent to opponent territory to flip on entry.
    candidates = []
    for (x, y) in unclaimed:
        if adj_to_enemy(x, y):
            candidates.append((x, y))

    # If none, go to closest unclaimed.
    if not candidates:
        candidates = unclaimed[:]

    # If still none, just move toward opponent.
    if not candidates:
        tx, ty = ox, oy
    else:
        # Deterministic scoring: prioritize adjacency, then closeness; slight bias toward staying away from obstacles isn't needed.
        best = None
        for (x, y) in candidates:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            # Small deterministic tie-break: prefer lower x then lower y
            score = (0 if adj_to_enemy(x, y) else 1, d, x, y)
            if best is None or score < best[0]:
                best = (score, (x, y))
        tx, ty = best[1]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # If we can step into opponent territory, that's very valuable.
        step_bonus = -100000 if (nx, ny) in enT else 0
        d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # If stepping into my territory, prefer not to stall (slight penalty).
        self_pen = 10 if (nx, ny) in myT else 0
        score = (step_bonus, d2, self_pen, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]