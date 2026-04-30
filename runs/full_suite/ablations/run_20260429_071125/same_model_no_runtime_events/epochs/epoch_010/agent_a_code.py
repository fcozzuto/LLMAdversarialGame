def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    best = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue

            target = res[0] if res else (sx, sy)
            if res:
                best_target = target
                best_td = dist(sx, sy, target[0], target[1])
                for rx, ry in res[1:]:
                    td = dist(sx, sy, rx, ry)
                    if td < best_td:
                        best_td = td
                        best_target = (rx, ry)
                target = best_target

            my_to_target = dist(nx, ny, target[0], target[1])
            my_to_opp = dist(nx, ny, ox, oy)
            opp_to_my = dist(ox, oy, nx, ny)

            near_resource_bonus = 10 if res and my_to_target == 0 else 0
            step_toward = 0
            if res:
                prev_to_target = dist(sx, sy, target[0], target[1])
                step_toward = prev_to_target - my_to_target

            score = 3 * step_toward - 0.8 * my_to_opp + 0.6 * opp_to_my + near_resource_bonus

            if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
                best_score = score
                best = [dx, dy]

    return best