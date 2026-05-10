def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    self_set = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    opp_set = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def score_cell(x, y):
        if not inb(x, y) or (x, y) in obst:
            return -10**9
        if (x, y) in self_set:
            base = 5
        elif (x, y) in opp_set:
            base = 120  # prefer flipping on contact
        else:
            base = 70   # unclaimed expansion
        d_to_opp = abs(x - ox) + abs(y - oy)
        d_to_me = abs(x - sx) + abs(y - sy)
        return base - 0.15 * d_to_opp - 0.02 * d_to_me

    # Prefer taking a move that expands to the best immediate destination.
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        s = score_cell(nx, ny)
        if s > best[0]:
            best = (s, dx, dy)

    # If no immediate good move (e.g., trapped), head to nearest unclaimed cell deterministically.
    if best[0] < 0:
        if unclaimed:
            # Choose nearest unclaimed, tie-break by preference to opponent proximity then direction.
            best_t = None
            for x, y in unclaimed:
                if (x, y) in obst:
                    continue
                cand = (abs(x - sx) + abs(y - sy), abs(x - ox) + abs(y - oy), x, y)
                if best_t is None or cand < best_t[0]:
                    best_t = (cand, x, y)
            tx, ty = best_t[1], best_t[2]
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0 if ty == sy else (1 if ty > sy else -1)
            if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obst:
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best[1]), int(best[2])]