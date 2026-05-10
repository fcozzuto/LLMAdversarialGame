def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Build deterministic targets: prioritize cells adjacent to opponent territory (including opponent cells), else unclaimed.
    targets = []
    if opp_terr:
        neigh = set()
        for px, py in opp_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    q = (px + dx, py + dy)
                    if inb(q[0], q[1]) and q not in opp_terr:
                        neigh.add(q)
        # Prefer entering opponent territory for flipping, so include opp_terr as high-value targets.
        targets = list(neigh) + list(opp_terr)
    if not targets:
        targets = unclaimed if unclaimed else [(sx, sy)]

    # Choose a single nearest target to steer toward.
    tx, ty = sx, sy
    best_td = None
    for q in targets:
        td = manh(sx, sy, q[0], q[1])
        if best_td is None or td < best_td or (td == best_td and (q[0], q[1]) < (tx, ty)):
            best_td = td
            tx, ty = q[0], q[1]

    def next_state_score(nx, ny):
        # Base desirability of occupying the next cell
        if (nx, ny) in opp_terr:
            base = 10.0
        elif (nx, ny) in unclaimed:
            base = 4.5
        elif (nx, ny) in self_terr:
            base = 1.0
        else:
            base = 0.2
        # Encourage moving closer to the chosen target
        dist = manh(nx, ny, tx, ty)
        # Mildly prefer reducing distance to any unclaimed (keeps pressure if target isn't perfect)
        un_d = None
        for ux, uy in unclaimed[:12]:
            d = manh(nx, ny, ux, uy)
            un_d = d if un_d is None or d < un_d else un_d
        if un_d is None:
            un_d = 99
        return base * 3.0 - dist * 0.9 - un_d * 0.05

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -1e9
        else:
            val = next_state_score(nx, ny)
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]