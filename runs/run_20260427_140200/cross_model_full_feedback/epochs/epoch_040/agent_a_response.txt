def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # No resources: move to maximize distance from opponent while staying legal
        best = (-(10**9), 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                score = dist(nx, ny, ox, oy)
                if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                    best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose move that improves "being closer than opponent" to the best available resource after our step
    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate by best resource we can potentially win (maximize opponent gap), break ties by favoring nearer
        best_res = None
        best_res_score = -(10**18)
        best_res_tie = (10**9, 10**9)
        for rx, ry in resources:
            d_me = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            gap = d_opp - d_me  # higher => we are closer than opponent
            # tie: prefer smaller d_me, then prefer smaller (d_opp - d_me)?? already gap; use d_opp
            tie = (d_me, d_opp)
            if gap > best_res_score or (gap == best_res_score and tie < best_res_tie):
                best_res_score = gap
                best_res_tie = tie
                best_res = (rx, ry)
        # Small extra preference: avoid giving opponent a big advantage by moving away from where they are going
        # Use also direct distance change to opponent.
        opp_diff = dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy)  # positive if we move away
        score = best_res_score * 1000 + opp_diff
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]