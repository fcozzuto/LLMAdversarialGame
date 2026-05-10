def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))

    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_manhattan(x, y, cells):
        if not cells:
            return 10**9
        best = 10**9
        # cap to keep deterministic and small
        cap = 24 if len(cells) > 24 else len(cells)
        for i in range(cap):
            cx, cy = cells[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    up = int(observation.get("self_territory_count") or 0)
    op = int(observation.get("opponent_territory_count") or 0)
    we_trail = up < op

    best_score = -10**18
    best_move = (0, 0)

    # precompute for heuristic targets
    un_list = unclaimed
    if not un_list:
        un_list = list(op_terr)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell_bonus = 0
        if (nx, ny) in self_terr:
            cell_bonus = 2
        elif (nx, ny) in op_terr:
            cell_bonus = 6
        elif (nx, ny) in set(unclaimed):
            cell_bonus = 5

        d_un = min_manhattan(nx, ny, un_list)
        d_opterr = min_manhattan(nx, ny, list(op_terr)[:24])
        d_opp = abs(nx - ox) + abs(ny - oy)

        # strategy switch:
        # - if trailing, push toward unclaimed/op territory
        # - if leading, keep expanding but avoid getting too close to opponent
        score = 10 * cell_bonus
        score += (-0.7 * d_un)
        score += (0.15 * d_opterr) if not we_trail else (-0.15 * d_opterr)
        score += (0.10 * d_opp) if not we_trail else (-0.05 * d_opp)

        # deterministic tie-break: smallest dx, then dy, with pref order already fixed in dirs
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]