def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in opp_set:
                    return True
        return False

    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))

    behind = myc < opc
    best = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cell = (nx, ny)
        sc = 0
        # Direct swing
        if cell in opp_set:
            sc += 50
        elif cell in unclaimed:
            sc += 18
        elif cell in self_set:
            sc += 2
        else:
            sc += 6

        # Cut off opponent by moving to cells that border their territory/unclaimed near them
        if adj_to_opp(nx, ny):
            sc += 12

        # Encourage closing distance when behind, otherwise drift to safe expansion
        d_opp = abs(nx - ox) + abs(ny - oy)
        sc += ( -d_opp if behind else -0.4 * d_opp )

        # Prefer reducing distance to nearest unclaimed frontier near opponent
        frontier = None
        md = 10**18
        for ux, uy in unclaimed:
            if not adj_to_opp(ux, uy):
                continue
            d = abs(ux - nx) + abs(uy - ny)
            if d < md:
                md = d
                frontier = (ux, uy)
        if frontier is not None:
            sc += 8 - 0.9 * md

        if sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]