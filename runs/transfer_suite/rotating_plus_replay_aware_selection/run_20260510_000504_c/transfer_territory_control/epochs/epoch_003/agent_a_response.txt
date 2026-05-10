def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = opp_pos[0], opp_pos[1]
    turn = observation.get("turn_index", 0)

    # Heuristic weights: prefer securing unclaimed, but actively counterclaim nearby opponent cells.
    un_list = list(unclaimed)
    opp_list = list(opp_terr)

    def best_dist(cell, targets, cap=16):
        if not targets:
            return 999
        x, y = cell
        best = 999
        n = 0
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
                if best == 0:
                    break
            n += 1
            if n >= cap and best == 1:
                break
        return best

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**12
        else:
            cell = (nx, ny)
            d_un = best_dist(cell, un_list)
            d_opp = best_dist(cell, opp_list)
            in_self = 1 if cell in self_terr else 0
            in_opp = 1 if cell in opp_terr else 0
            in_un = 1 if cell in unclaimed else 0

            # Encourage capturing immediately; also push toward closest targets.
            val = 0
            val += (10 if in_un else 0)
            val += (7 if in_opp else 0)  # flip-on-entry is enabled
            val += (2 if in_self else 0)
            val += -1.2 * d_un
            val += -1.0 * d_opp
            # Mild pressure toward opponent to prevent static play against counterclaimers.
            val += -0.05 * (abs(nx - ox) + abs(ny - oy))

            # Small deterministic center preference early to reduce being cornered by claims.
            if turn < 10:
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                val += -0.001 * ((nx - cx) ** 2 + (ny - cy) ** 2)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]