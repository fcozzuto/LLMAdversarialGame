def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource where we have the best (opponent_dist - self_dist) advantage
    best_r = None
    best_adv = None
    best_selfd = None
    opp_pos = (ox, oy)
    self_pos = (sx, sy)
    for r in resources:
        rd = (r[0], r[1])
        sd = dist(self_pos, rd)
        od = dist(opp_pos, rd)
        adv = od - sd
        sd_key = (sd, rd[0] * 31 + rd[1] * 17)
        if best_r is None or adv > best_adv or (adv == best_adv and (sd_key < (best_selfd, best_r[0] * 31 + best_r[1] * 17))):
            best_r, best_adv, best_selfd = rd, adv, sd

    target = best_r

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_d_to_t = dist(self_pos, target)
    cur_d_to_o = dist(self_pos, opp_pos)

    # If we are behind on best target, prioritize escaping and re-routing; if we are ahead, intercept opponent while going for target
    intercept = 1 if best_adv > 0 else 0
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        npos = (nx, ny)
        d_to_t = dist(npos, target)
        d_to_o = dist(npos, opp_pos)
        score = 0
        # Primary: minimize distance to target (and progress)
        score += (cur_d_to_t - d_to_t) * 10
        score += -d_to_t
        # Secondary: if we are ahead, move to reduce opponent distance too (contesting)
        if intercept:
            score += (cur_d_to_o - d_to_o) * 2 - d_to_o * 0.1
        # Tertiary: deterministic tie-break by coordinates
        score += -((nx * 7 + ny) * 1e-3)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]