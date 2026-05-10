def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs_set.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs_set.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs_set.add((int(p["x"]), int(p["y"])))

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res_list.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res_list.append((int(r["x"]), int(r["y"])))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    if not res_list:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            nx, ny = sx, sy
        if (nx, ny) in obs_set:
            nx, ny = sx, sy

        best_margin = -10**9
        best_self_d = 10**9
        for rx, ry in res_list:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d
            if margin > best_margin or (margin == best_margin and self_d < best_self_d) or (margin == best_margin and self_d == best_self_d and (rx + ry) < (best_rx + best_ry) if False else False):
                best_margin = margin
                best_self_d = self_d
        score = (best_margin, -best_self_d, -(nx * 16 + ny))
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]