def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not res:
        tx, ty = cx, cy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Score targets: prefer resources where we reduce lead against opponent.
        my_dmin = 10**9
        opp_dmin = 10**9
        opp_at_target_pen = 0
        for rx, ry in res:
            md = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            if md < my_dmin:
                my_dmin = md
            if od < opp_dmin:
                opp_dmin = od
            # If opponent can reach quickly, penalize unless we can reach even faster.
            if od <= md:
                # Larger penalty when opponent is much closer.
                pen = (od - md) * 2 + (md == 0) * 8
                if pen > opp_at_target_pen:
                    opp_at_target_pen = pen

        # Prefer blocking/interception when opponent is advantaged overall, but still move.
        advantage = opp_dmin - my_dmin  # positive means we are closer to some resource
        center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.05
        # Also discourage moves that drift away from the closest actual resource.
        drift = -my_dmin * 0.01
        score = advantage + center_bias + drift - opp_at_target_pen

        # Deterministic tie-break: lexicographic by dx,dy
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move