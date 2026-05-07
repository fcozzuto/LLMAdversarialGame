def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)
    env = observation.get("environment_name", "resource_collection")
    if env != "resource_collection":
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Pick a resource where we are relatively closer than the opponent; if tie, prefer closer to us, then lexicographic.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Larger (od-sd) => we have advantage. Convert to minimization key.
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No available resources: move toward opponent.
        tx, ty = ox, oy
    else:
        tx, ty = best

    # If opponent is already very close to a resource, we try to "intercept" by targeting the resource with best advantage.
    # Then choose a move maximizing a deterministic local heuristic.
    opp_min = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        od = dist2(ox, oy, rx, ry)
        if opp_min is None or od < opp_min:
            opp_min = od
    # Local move scoring.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        # Prefer reducing distance to target.
        d_to = dist2(nx, ny, tx, ty)
        d_self = dist2(nx, ny, sx, sy)
        # Discourage moving away too much; encourage staying roughly directed.
        direction_bonus = 0
        # If we move closer to target than opponent would, slight boost.
        opp_next = (ox + dx if inb(ox + dx, oy) else ox, oy + dy if inb(ox, oy + dy) else oy)
        opp_est = dist2(opp_next[0], opp_next[1], tx, ty)
        # Obstacle-pressure: moving adjacent to obstacles is slightly penalized to avoid tight traps.
        adj_obs = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in obs_set:
                adj_obs += 1
        score = (-d_to) + (-0.01 * d_self) + (0.05 if d_to < opp_est else 0) - (0.15 * adj_obs)
        # If opponent is close to any resource, slightly favor moves that improve our relative advantage.
        if opp_min is not None:
            my_adv = dist2(nx, ny, tx, ty) - dist2(ox, oy, tx, ty)
            score += -0.02 * my_adv
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]