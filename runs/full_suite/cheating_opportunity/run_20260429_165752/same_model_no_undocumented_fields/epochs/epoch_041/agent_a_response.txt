def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cur_pos = (sx, sy)
    opp_pos = (ox, oy)

    best_res = None
    if resources:
        best_res = min(resources, key=lambda r: (dist(cur_pos, r), cheb(opp_pos, r), r[0], r[1]))

    # Deterministic move scoring:
    # - Go toward a selected target resource (or generally toward any resource if no target chosen)
    # - If opponent is closer to the target, increase priority to intercept by moving to reduce opponent distance more
    # - Avoid moving too close to opponent
    best_move = legal[0]
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        npos = (nx, ny)

        if resources:
            if best_res is not None:
                target = best_res
            else:
                target = min(resources, key=lambda r: (dist(npos, r), r[0], r[1]))

            d_me = dist(npos, target)
            d_opp = dist(opp_pos, target)

            # How much we improve over opponent regarding the target
            my_adv = d_opp - d_me  # larger is better
            opp_after = dist(npos, opp_pos)  # closeness penalty

            # Small tie-break to prefer progressing in x then y deterministically
            tie = -(abs(target[0] - nx) + 2 * abs(target[1] - ny))

            # Being adjacent to opponent is risky; being farther is safer
            safety = -2 * cheb(npos, opp_pos)

            score = 30 * my_adv + safety + 3 * tie
        else:
            # No resources: drift away from opponent while keeping within bounds
            score = -2 * cheb(npos, opp_pos) + (- (nx * 0 + ny * 0)) + (- (dx * 0 + dy * 0))

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]