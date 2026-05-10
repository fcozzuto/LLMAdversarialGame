def choose_move(observation):
    x, y = observation.get("self_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_count(cell_set, nx, ny):
        c = 0
        for dx, dy in dirs8:
            tx, ty = nx + dx, ny + dy
            if (tx, ty) in cell_set:
                c += 1
        return c

    # Deterministic "expansion": prefer unclaimed near our territory, then safe approach to opponent edges.
    best_move = (0, 0)
    best_v = -10**18

    # Precompute a simple direction bias using closest relevant cell (unclaimed or opponent territory).
    targets = []
    if unclaimed:
        targets = list(unclaimed)
    elif opp_terr:
        targets = list(opp_terr)

    tx0, ty0 = x, y
    if targets:
        best_t = None
        best_td = None
        for tx, ty in targets:
            if (tx, ty) in obstacles:
                continue
            td = (abs(tx - x) + abs(ty - y), abs(tx - x) + abs(ty - y) + 3 * abs(tx - x - (observation.get("opponent_position", (0, 0))[0] - x)))
            if best_td is None or td < best_td:
                best_td = td
                best_t = (tx, ty)
        if best_t is not None:
            tx0, ty0 = best_t

    for dx, dy in [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        v = 0
        if (nx, ny) in self_terr:
            v += 8 * adj_count(self_terr, nx, ny)
            v += 1.5 * adj_count(opp_terr, nx, ny)  # keep near action
        elif (nx, ny) in unclaimed:
            v += 220
            v += 6 * adj_count(self_terr, nx, ny)
            v -= 3 * adj_count(opp_terr, nx, ny)
            # bias toward overall expansion direction
            v -= 0.8 * (abs(tx0 - nx) + abs(ty0 - ny))
        elif (nx, ny) in opp_terr:
            # only claim if it increases local advantage
            my_a = adj_count(self_terr, nx, ny)
            op_a = adj_count(opp_terr, nx, ny)
            v += 260 + 30 * (my_a - op_a)
            v -= 2 * (abs(tx0 - nx) + abs(ty0 - ny))
        else:
            # empty cell: try to move toward unclaimed/opponent with minimal risk
            v += 5 * adj_count(self_terr, nx, ny)
            v -= 2 * adj_count(opp_terr, nx, ny)
            v -= 0.5 * (abs(tx0 - nx) + abs(ty0 - ny))

        # Tie-break deterministically: prefer moves that reduce distance to target, then lexicographic.
        if v > best_v:
            best_v = v
            best_move = (dx, dy)
        elif v == best_v:
            dcur = abs(tx0 - nx) + abs(ty0 - ny)
            dbest = abs(tx0 - (x + best_move[0])) + abs(ty0 - (y + best_move[1]))
            if dcur < dbest or (dcur == dbest and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]