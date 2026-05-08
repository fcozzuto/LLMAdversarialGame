def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_evader = "evader" in sr
    opp_evader = "evader" in orr
    self_pursuer = not self_evader
    if (not sr and "evader" in orr) or (sr == "" and not opp_evader):
        self_pursuer = True

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        opp_dist = d2(nx, ny, ox, oy)
        if self_pursuer:
            opp_term = -opp_dist
        else:
            opp_term = opp_dist

        res_term = 0
        if resources:
            best_res = min(d2(nx, ny, rx, ry) for rx, ry in resources)
            if self_pursuer:
                res_term = -best_res
            else:
                res_term = -0.5 * best_res

        score = opp_term + res_term
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]