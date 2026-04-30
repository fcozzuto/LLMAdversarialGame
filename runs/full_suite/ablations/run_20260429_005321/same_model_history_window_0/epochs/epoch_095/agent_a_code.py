def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = observation["obstacles"]
    obstacle_set = {(p[0], p[1]) for p in obstacles}
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        tx, ty = w//2, h//2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacle_set or nx < 0 or nx >= w or ny < 0 or ny >= h:
            return [0, 0]
        return [dx, dy]
    # Choose target by comparing who is closer (greedy, deterministic)
    def manh(a, b, c, d):
        return abs(a-c) + abs(b-d)
    targets = []
    for r in resources:
        rx, ry = r
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; break ties by position
        # Larger score is better
        targets.append((do - ds, -rx, -ry, rx, ry))
    targets.sort(reverse=True)
    _, _, _, tx, ty = targets[0]

    best = None
    # Evaluate each move by improvement toward our target while discouraging opponent access to resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacle_set:
            continue
        # Main objective: reduce distance to chosen target
        d_self = manh(nx, ny, tx, ty)
        # Secondary: how close opponent is to the best alternative after our move
        best_opp = 10**9
        # Consider only the top few resources for efficiency/determinism
        for r in targets[:5]:
            rx, ry = r[3], r[4]
            best_opp = min(best_opp, manh(ox, oy, rx, ry))
        # Discourage moves that leave our position allowing opponent to be much closer to some resource
        # Also slightly prefer moves that reduce opponent distance to their nearest resource
        # (prevents walking into "hand-off" situations)
        d_opp = best_opp
        score = (-d_self) - 0.15 * d_opp + 0.01 * (dx + dy)  # deterministic tie-break via dx+dy
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[1], best[2]]