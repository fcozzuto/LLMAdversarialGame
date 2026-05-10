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
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    neigh8 = [(-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed_list = list(unclaimed)
    def dist_to_nearest_unclaimed(x, y):
        if not unclaimed_list:
            return 10**6
        best = 10**6
        cap = 40 if len(unclaimed_list) > 40 else len(unclaimed_list)
        for i in range(cap):
            cx, cy = unclaimed_list[i]
            d = abs(cx - x) + abs(cy - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            score = -10**9
        else:
            adj_un = 0
            adj_op = 0
            adj_obs = 0
            for ax, ay in neigh8:
                tx, ty = nx + ax, ny + ay
                if not inb(tx, ty):
                    continue
                if (tx, ty) in unclaimed:
                    adj_un += 1
                if (tx, ty) in op_terr:
                    adj_op += 1
                if (tx, ty) in obstacles:
                    adj_obs += 1
            score = 0
            if (nx, ny) in unclaimed:
                score += 12
            if (nx, ny) in op_terr:
                score += 9
            if (nx, ny) in self_terr:
                score += 2
            score += 5 * adj_un
            score -= 3 * adj_op
            score -= 2 * adj_obs
            score -= 0.15 * dist_to_nearest_unclaimed(nx, ny)

            lead_self = int(observation.get("self_territory_count") or 0)
            lead_op = int(observation.get("opponent_territory_count") or 0)
            if lead_self < lead_op and (nx, ny) in op_terr:
                score += 3
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move