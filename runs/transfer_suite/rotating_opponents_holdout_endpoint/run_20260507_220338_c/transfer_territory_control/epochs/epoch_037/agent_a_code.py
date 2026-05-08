def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))
        except:
            pass

    if not unclaimed:
        return [0, 0]

    best_t = None
    best_d = None
    for x, y in unclaimed:
        d = abs(x - sx) + abs(y - sy)
        if best_d is None or d < best_d or (d == best_d and (x < best_t[0] or (x == best_t[0] and y < best_t[1]))):
            best_d = d
            best_t = (x, y)
    tx, ty = best_t

    moves = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(ox - nx) + abs(oy - ny)
        score = (dist, -opp_dist, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]