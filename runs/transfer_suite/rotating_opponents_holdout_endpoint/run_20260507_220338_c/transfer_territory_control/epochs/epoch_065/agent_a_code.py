def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set(tuple(t) for t in (observation.get("self_territory") or []))
    opp_terr = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(t) for t in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocks

    def border_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    opp_list = list(opp_terr)
    def nearest_opp_cell_dist(nx, ny):
        if not opp_list:
            return abs(nx - ox) + abs(ny - oy)
        best = None
        for px, py in opp_list:
            d = abs(nx - px) + abs(ny - py)
            if best is None or d < best:
                best = d
        return best if best is not None else (abs(nx - ox) + abs(ny - oy))

    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            cell_score = 30
        elif (nx, ny) in unclaimed:
            cell_score = 16
        elif (nx, ny) in self_terr:
            cell_score = 6
        else:
            cell_score = 8  # likely something else; still prefer progress

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_near_opp_cell = nearest_opp_cell_dist(nx, ny)
        bd = border_dist(nx, ny)

        # Higher is better. Deterministic tie-break via tuple ordering.
        key = (-cell_score, d_to_opp, d_near_opp_cell, bd, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]