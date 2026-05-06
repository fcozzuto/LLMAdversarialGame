def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w // 2, h // 2)

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs

    best_move = (0, 0)
    best_score = -10**18

    # Choose next step that maximizes advantage over opponent for the best resource
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        my_d_center = dist((nx, ny), center)
        opp_d_center = dist((ox, oy), center)

        # Evaluate best resource for us after this move
        best_gap = -10**9
        best_my = 10**9
        best_r_op = 10**9
        for r in resources:
            md = dist((nx, ny), r)
            od = dist((ox, oy), r)
            gap = od - md  # positive means we arrive sooner than opponent
            # prefer positive gaps; tie-break by smaller my distance
            if gap > best_gap or (gap == best_gap and md < best_my) or (gap == best_gap and md == best_my and od < best_r_op):
                best_gap = gap
                best_my = md
                best_r_op = od

        # Score: prioritize winning a resource gap; slight center bias to keep pressure
        score = best_gap * 1000 - best_my * 5 + (opp_d_center - my_d_center)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]