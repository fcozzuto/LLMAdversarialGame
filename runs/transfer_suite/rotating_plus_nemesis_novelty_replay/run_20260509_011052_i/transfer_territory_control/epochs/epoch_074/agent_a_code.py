def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    res = []
    for p in (observation.get("resources", []) or []):
        try:
            res.append((int(p[0]), int(p[1])))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    nearest_res = None
    if res:
        d0 = 10**9
        for rx, ry in res:
            d = abs(rx - sx) + abs(ry - sy)
            if d < d0:
                d0 = d
                nearest_res = (rx, ry)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if nearest_res is not None:
            dist_res = abs(nearest_res[0] - nx) + abs(nearest_res[1] - ny)
            dist_opp = abs(ox - nx) + abs(oy - ny)
            score = -dist_res * 1000 + dist_opp
        else:
            dist_opp = abs(ox - nx) + abs(oy - ny)
            score = dist_opp * 1000
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]