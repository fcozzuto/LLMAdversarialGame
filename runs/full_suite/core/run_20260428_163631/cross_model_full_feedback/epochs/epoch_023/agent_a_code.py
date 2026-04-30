def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    opp_to = resources if resources else [(ox, oy)]
    best = None
    best_score = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            my_min = 10**9
            best_margin = -10**9
            for rx, ry in resources:
                dm = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if dm < my_min:
                    my_min = dm
                margin = do - dm
                if margin > best_margin:
                    best_margin = margin
            score = best_margin * 100 - my_min
        else:
            # No resources seen: advance toward opponent to contest territory.
            score = -cheb(nx, ny, ox, oy)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]