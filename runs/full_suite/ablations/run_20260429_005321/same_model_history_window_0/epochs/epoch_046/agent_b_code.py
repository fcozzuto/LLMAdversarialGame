def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(nx, ny):
        if nx < 0:
            nx = 0
        elif nx >= w:
            nx = w - 1
        if ny < 0:
            ny = 0
        elif ny >= h:
            ny = h - 1
        return nx, ny

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_pos(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if resources:
            best_adv = -10**9
            best_me = 10**9
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                adv = d_opp - d_me  # positive if I'm closer than opponent
                if adv > best_adv or (adv == best_adv and d_me < best_me):
                    best_adv = adv
                    best_me = d_me
            # Encourage immediate progress while strongly preferring positions that flip advantage.
            # Also slightly prefer moves that increase distance from opponent to reduce contesting turn gains.
            dist_to_opp = cheb(nx, ny, ox, oy)
            return best_adv * 1000 - best_me * 10 + dist_to_opp
        # No resources: drift toward center
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        dx = nx - cx
        if dx < 0:
            dx = -dx
        dy = ny - cy
        if dy < 0:
            dy = -dy
        return -(dx + dy)

    best = None
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = clamp(myx + dx, myy + dy)
        sc = score_pos(nx, ny)
        if sc > best_score:
            best_score = sc
            best = [dx, dy]
    return best