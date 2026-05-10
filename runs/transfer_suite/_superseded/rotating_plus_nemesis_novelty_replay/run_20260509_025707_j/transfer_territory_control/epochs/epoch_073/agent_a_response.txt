def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    self_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    myc = observation.get("self_territory_count", len(self_set))
    opc = observation.get("opponent_territory_count", len(opp_set))
    behind = (myc < opc)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_opp(x, y):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in opp_set:
                    return 1
        return 0

    opp_list = list(opp_set)
    opp_cx = 3.5
    opp_cy = 3.5
    if opp_list:
        sxm = 0
        sym = 0
        for x, y in opp_list:
            sxm += x
            sym += y
        opp_cx = sxm / len(opp_list)
        opp_cy = sym / len(opp_list)

    def dist_to_opp_cent(x, y):
        dx = x - opp_cx
        dy = y - opp_cy
        return (dx * dx + dy * dy) ** 0.5

    best = (-10**18, 0, 0)
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                if dx == 0 and dy == 0:
                    pass
                else:
                    continue
            cell = 0
            if (nx, ny) in opp_set:
                cell += 28 if behind else 22
            elif (nx, ny) in unclaimed:
                cell += 16 if behind else 12
                cell += 6 * adj_to_opp(nx, ny)
            elif (nx, ny) in self_set:
                cell += 6
            else:
                cell += 2

            d = dist_to_opp_cent(nx, ny)
            cell += -d * (2.2 if behind else 1.5)

            # Encourage widening: prefer moves that are closer to the center unclaimed/opponent boundary
            cx = 3.5
            cy = 3.5
            dc = abs(nx - cx) + abs(ny - cy)
            cell += -0.15 * dc

            if cell > best[0]:
                best = (cell, dx, dy)
            elif cell == best[0]:
                # deterministic tie-break
                if (dx, dy) < (best[1], best[2]):
                    best = (cell, dx, dy)

    return [int(best[1]), int(best[2])]