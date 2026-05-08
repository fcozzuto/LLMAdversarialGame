def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    self_terr = set()
    for p in observation.get("self_territory") or []:
        try:
            self_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        try:
            opp_terr.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        try:
            unclaimed.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy, best_val = 0, 0, -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 5.0
        elif (nx, ny) in self_terr:
            val += 1.5
        elif (nx, ny) in unclaimed:
            val += 2.0
        else:
            val += 0.2

        ddx, ddy = nx - cx, ny - cy
        val += 0.35 * (ddx * ddx + ddy * ddy)  # prefer edges/corners vs center
        opp_dist = abs(nx - ox) + abs(ny - oy)
        val += -0.08 * opp_dist               # stay away from opponent pressure
        if opp_dist == 0:
            val -= 3.0

        if val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]