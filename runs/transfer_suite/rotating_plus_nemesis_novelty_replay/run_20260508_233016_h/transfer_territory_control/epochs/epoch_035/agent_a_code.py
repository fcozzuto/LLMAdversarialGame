def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation["opponent_position"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_point(src, points):
        if not points:
            return None
        best = None
        bd = 10**9
        for px, py in points:
            d = abs(px - src[0]) + abs(py - src[1])
            if d < bd:
                bd = d
                best = (px, py)
        return best

    opp_target = nearest_point((sx, sy), opp_terr) or nearest_point((sx, sy), unclaimed) or (w // 2, h // 2)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**9 - (1 if (dx != 0 or dy != 0) else 0)
        else:
            cell = (nx, ny)
            val = 0.0

            if cell in opp_terr:
                val += 7.5
            elif cell in unclaimed:
                val += 4.2
            elif cell in self_terr:
                val += 1.2

            adj_opp = 0
            adj_self = 0
            for ax, ay in neigh:
                xx, yy = nx + ax, ny + ay
                if not inb(xx, yy) or (xx, yy) in obstacles:
                    continue
                if (xx, yy) in opp_terr:
                    adj_opp += 1
                if (xx, yy) in self_terr:
                    adj_self += 1
            val += adj_opp * 1.6
            val += adj_self * 0.7

            if (dx, dy) == (0, 0):
                val -= 0.9

            val += -0.25 * dist(cell, opp_target)
            val += 0.08 * dist(cell, (ox, oy))

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]