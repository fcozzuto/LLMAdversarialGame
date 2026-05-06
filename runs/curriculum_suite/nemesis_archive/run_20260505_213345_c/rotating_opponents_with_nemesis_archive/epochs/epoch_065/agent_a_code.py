def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    resset = set()
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                resset.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    cur_opp_d = cheb((sx, sy), (ox, oy))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        opp_d = cheb(pos, (ox, oy))
        away_bonus = opp_d - cur_opp_d  # prefer distancing from opponent

        # resource pressure
        val = 0
        if pos in resset:
            val += 10000
        else:
            local = -10 * cheb(pos, (sx, sy))  # discourage wandering
            gain = -10 * opp_d  # discourage getting too close in general
            # choose best target from this position, favoring resources where we beat the opponent
            best_t = None
            for r in resources:
                sd = cheb(pos, r)
                od = cheb((ox, oy), r)
                if best_t is None or (od - sd) > (best_t[0] - best_t[1]) or ((od - sd) == (best_t[0] - best_t[1]) and sd < best_t[1]):
                    best_t = (od, sd)
            if best_t is not None:
                od, sd = best_t
                # if we can arrive first, prioritize strongly; otherwise still push toward high-advantage targets
                if sd <= od:
                    local += (od - sd + 1) * 220
                else:
                    local += (od - sd) * 120
                gain += (od - sd) * 20
            val += local + gain

        val += away_bonus * 30

        if best_score is None or val > best_score:
            best_score = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best