def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    if not res:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    k = 0.85  # favor races where we have distance advantage
    best_move = (0, 0)
    best_score = 10**9
    best_selfdist = 10**9
    best_oppdist = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        cur_best_score = 10**9
        cur_best_sd = 10**9
        cur_best_od = 10**9

        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # lower is better: our distance, penalized if opponent is also near/closer
            score = sd - k * od
            if score < cur_best_score:
                cur_best_score = score
                cur_best_sd = sd
                cur_best_od = od
            elif score == cur_best_score:
                if sd < cur_best_sd:
                    cur_best_sd, cur_best_od = sd, od
                elif sd == cur_best_sd and od < cur_best_od:
                    cur_best_od = od

        # discourage "no progress" unless it's clearly best
        if (dx, dy) == (0, 0) and cur_best_score > best_score:
            continue

        if cur_best_score < best_score:
            best_score = cur_best_score
            best_selfdist = cur_best_sd
            best_oppdist = cur_best_od
            best_move = (dx, dy)
        elif cur_best_score == best_score:
            if cur_best_sd < best_selfdist:
                best_selfdist = cur_best_sd
                best_oppdist = cur_best_od
                best_move = (dx, dy)
            elif cur_best_sd == best_selfdist and cur_best_od < best_oppdist:
                best_oppdist = cur_best_od
                best_move = (dx, dy)
            elif cur_best_sd == best_selfdist and cur_best_od == best_oppdist:
                if (dx, dy) != (0, 0) and best_move == (0, 0):
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]