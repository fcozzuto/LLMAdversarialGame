def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    moves.append((0, 0))

    if resources:
        tx, ty = resources[0]
        target = (tx, ty)
    else:
        frontier = []
        for x, y in self_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        frontier.append((nx, ny))
        if frontier:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            ox, oy = observation["opponent_position"]
            # Prefer: near our frontier, slightly toward center, and not giving up too much distance to opponent
            target = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy), abs(p[0] - ox) + abs(p[1] - oy)))
        else:
            # If no frontier, go to nearest unclaimed, else toward center
            if unclaimed:
                target = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
            else:
                target = ((w - 1) // 2, (h - 1) // 2)

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_cell(x, y):
        # Higher is better for moving into (territory flipping on entry)
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in opp_terr:
            s += 120  # likely flip value
        if (x, y) in unclaimed:
            s += 60   # safe expansion
        # Reduce distance to target
        s += 25 - manhattan((x, y), target)
        # Mild preference toward center to avoid getting boxed
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        s += -0.05 * (abs(x - cx) + abs(y - cy))
        return s

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            sc = -10**9
        else:
            sc = score_cell(nx, ny)
            # If moving into opponent is possible, strongly favor adjacency to opponent to force flips
            if (nx, ny) in opp_terr:
                sc += 40
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_move):
            best_sc = sc
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]