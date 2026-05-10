def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    un_list = list(unclaimed)
    res_list = list(resources)
    opp_list = list(opp_terr)

    def nearest_dist(x, y, cells):
        if not cells:
            return 10**9
        best = 10**9
        for tx, ty in cells[:32]:
            d = manhattan(x, y, tx, ty)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    target_cells = un_list if un_list else (res_list if res_list else [])
    dist_to_target_now = nearest_dist(sx, sy, target_cells)
    opp_dist_now = nearest_dist(sx, sy, opp_list)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in unclaimed:
            val += 8.0
        elif (nx, ny) in opp_terr:
            val += 5.0
        elif (nx, ny) in self_terr:
            val += 3.0
        else:
            val += 1.0

        dist_to_target_next = nearest_dist(nx, ny, target_cells)
        if dist_to_target_next < dist_to_target_now:
            val += 4.0
        elif dist_to_target_next == dist_to_target_now:
            val += 1.0
        else:
            val -= 1.0

        opp_dist_next = nearest_dist(nx, ny, opp_list)
        if opp_dist_next < opp_dist_now:
            val -= 1.2
        else:
            val += 0.6

        val -= 0.06 * manhattan(nx, ny, ox, oy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]