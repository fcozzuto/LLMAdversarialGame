def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            x, y = p
        except Exception:
            continue
        obstacles.add((int(x), int(y)))

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, dict):
            x = r.get("x", r.get("position", (0, 0))[0])
            y = r.get("y", r.get("position", (0, 0))[1])
        else:
            try:
                x, y = r
            except Exception:
                continue
        tx, ty = int(x), int(y)
        if 0 <= tx < w and 0 <= ty < h:
            targets.append((tx, ty))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if targets:
        best = None
        target = targets[0]
        for rx, ry in targets:
            my_d = md(sx, sy, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            pr = (my_d - opp_d, my_d, -rx, -ry)
            if best is None or pr < best:
                best = pr
                target = (rx, ry)
        tx, ty = target
        best_move = (0, 0)
        best_pr = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d1 = md(nx, ny, tx, ty)
            d2 = md(nx, ny, ox, oy)
            pr = (d1, -d2, dx, dy)
            if best_pr is None or pr < best_pr:
                best_pr = pr
                best_move = (dx, dy)
        dx, dy = best_move
        return [int(dx), int(dy)]
    else:
        # No resources: move to increase distance from opponent.
        best_pr = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            pr = (-md(nx, ny, ox, oy), dx, dy)
            if best_pr is None or pr < best_pr:
                best_pr = pr
                best_move = (dx, dy)
        dx, dy = best_move
        return [int(dx), int(dy)]