def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacle_set

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def obs_pen(x, y):
        # penalty for being adjacent to obstacles
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacle_set:
                    p += 1
        return p

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    best_tiebreak = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # lookahead: from this next cell, choose the resource that maximizes our lead
        cur_best_adv = -10**18
        cur_best_sd = 10**18
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            if adv > cur_best_adv or (adv == cur_best_adv and sd < cur_best_sd):
                cur_best_adv = adv
                cur_best_sd = sd

        val = cur_best_adv - 0.35 * obs_pen(nx, ny) - 0.02 * cur_best_sd
        tieb = cur_best_sd
        if val > best_val or (val == best_val and tieb < best_tiebreak):
            best_val = val
            best_tiebreak = tieb
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]