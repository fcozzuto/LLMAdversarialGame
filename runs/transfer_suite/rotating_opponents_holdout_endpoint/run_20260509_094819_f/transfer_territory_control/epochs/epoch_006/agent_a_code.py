def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = opp_pos[0], opp_pos[1]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target: favor unclaimed near our territory; if none, push toward opponent.
    targets = list(unclaimed)
    if self_terr:
        near_self = []
        for x, y in targets:
            best_adj = 10**9
            for dx, dy in dirs:
                ax, ay = x + dx, y + dy
                if (ax, ay) in self_terr:
                    best_adj = 0
                    break
            near_self.append((0 if best_adj == 0 else 1, manh(x, y, sx, sy), x, y))
        near_self.sort(key=lambda t: (t[0], t[1], t[3], t[2]))
        targets = [(t[2], t[3]) for t in near_self[:10]]
    else:
        targets.sort(key=lambda p: (manh(p[0], p[1], sx, sy), p[1], p[0]))
        targets = targets[:10]

    best_t = None
    if targets:
        best_t = min(targets, key=lambda p: (manh(p[0], p[1], sx, sy), p[1], p[0]))
    else:
        best_t = (ox, oy)

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**12
        s = 0
        if (nx, ny) in unclaimed:
            s += 20
        if (nx, ny) in opp_terr:
            # Flipping on entry is good; add more if it can connect to our territory or cut them.
            s += 16
        if (nx, ny) in self_terr:
            s -= 1

        # Move toward the main target
        s += 6 - manh(nx, ny, best_t[0], best_t[1])

        # Frontier logic: prefer cells adjacent to our territory (expand) or adjacent to opponent territory (combat).
        adj_self = 0
        adj_opp = 0
        for dx, dy in dirs:
            ax, ay = nx + dx, ny + dy
            if not inb(ax, ay):
                continue
            if (ax, ay) in self_terr or (ax, ay) == (sx, sy):
                adj_self += 1
            if (ax, ay) in opp_terr:
                adj_opp += 1
        s += adj_self * 3
        s += adj_opp * 4

        # Light anti-trap: discourage stepping far from our current position when target is far.
        s -= (manh(nx, ny, sx, sy) > 2) * 2
        return s

    best_move = [0, 0]
    best_score = -10**18
    # Tie-break deterministically by direction ordering.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]
    return best_move