def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evasion" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    wall_target = (0, 0)
    if not i_am_evader:
        wall_target = (7, 7)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    obs_list = list(obstacles)
    def nearest_obst_d2(x, y):
        if not obs_list:
            return 999999
        best = 999999
        for ax, ay in obs_list:
            d = dist2(x, y, ax, ay)
            if d < best:
                best = d
        return best

    best_move = [0, 0]
    best_score = -10**18 if i_am_evader else -10**18

    # Deterministic tie-break order: by (score, dx, dy) with fixed dir ordering.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_opp_cur = dist2(sx, sy, ox, oy)
        d_delta = d_opp - d_opp_cur

        # wall hugging: prefer being near any border for evader; for pursuer avoid corners poorly.
        near_wall = min(nx, ny, w - 1 - nx, h - 1 - ny)
        wall_score = (7 - near_wall)  # bigger when closer to wall

        # obstacle avoidance: keep distance
        obs_d2 = nearest_obst_d2(nx, ny)
        obs_score = obs_d2  # larger is better

        # Corner baiting for evader: bias toward farthest corner from opponent but only via wall proximity proxy.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        corner_dist = dist2(nx, ny, far_corner[0], far_corner[1])
        corner_score = -corner_dist if i_am_evader else corner_dist

        score = 0
        if i_am_evader:
            score = (d_delta * 2000) + (wall_score * 30) + (obs_score * 0.01) + (corner_score * 0.5)
        else:
            # pursuer: reduce distance, and avoid obstacles strongly
            score = (-d_delta * 2000) + (-wall_score * 2) + (obs_score * 0.01) + (-corner_score * 0.1)

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback if all moves blocked (should be rare): stay still.
    return best_move if valid(sx + best_move[0], sy + best_move[1]) else [0, 0]