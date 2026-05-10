def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = myc < opc

    # Precompute nearest unclaimed distance (small constant search)
    un_list = list(unclaimed)
    closest_un_dist = 99
    if un_list:
        for p in un_list:
            d = manh((sx, sy), p)
            if d < closest_un_dist:
                closest_un_dist = d

    def adj_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    best = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)

        sc = 0

        # Immediate swing/contain
        if cell in opp_set:
            sc += 18 if behind else 14
        elif cell in unclaimed:
            sc += 7 if behind else 8
        elif cell in self_set:
            sc += 2

        # Frontier pressure
        if adj_opp(nx, ny):
            sc += 4 if behind else 3

        # Distance shaping
        if un_list:
            d_un = 99
            for p in un_list:
                dd = manh((nx, ny), p)
                if dd < d_un:
                    d_un = dd
            if d_un < closest_un_dist:
                sc += 2
            sc += (10 - d_un) * (1 if behind else 0.7)

        # Stay slightly penalized unless it is safest
        if dx == 0 and dy == 0:
            sc -= 1

        # Avoid moving into "dead" cells (no adjacent free cells)
        free_adj = 0
        for mx, my in moves:
            ax, ay = nx + mx, ny + my
            if inb(ax, ay):
                free_adj += 1
        sc += 0.5 if free_adj >= 3 else (-1.5 if free_adj <= 1 else 0)

        # Deterministic tie-break
        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]