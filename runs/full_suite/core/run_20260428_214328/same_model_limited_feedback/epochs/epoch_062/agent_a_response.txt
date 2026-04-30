def choose_move(observation):
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def step_valid(x,y): return inb(x,y) and (x,y) not in obstacles

    if not resources:
        # Go to center-ish to reduce opponent advantage deterministically
        tx, ty = (w-1)//2, (h-1)//2
    else:
        best = None
        # Deny strategy: pick a resource where opponent is closer; break ties by distance to opponent
        for (rx, ry) in resources:
            ds = max(abs(rx - sx), abs(ry - sy))
            do = max(abs(rx - ox), abs(ry - oy))
            score = (0 if do <= ds else 1, do - ds, do, ds, (rx+ry) % 7)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        _, tx, ty = best

    # If target already at/near, shift to next closest by self to avoid stalling
    if max(abs(tx - sx), abs(ty - sy)) == 0 and resources:
        best2 = None
        for (rx, ry) in resources:
            ds = max(abs(rx - sx), abs(ry - sy))
            do = max(abs(rx - ox), abs(ry - oy))
            score = (0 if ds <= do else 1, ds, do, (rx*3+ry) % 5)
            if best2 is None or score < best2[0]:
                best2 = (score, rx, ry)
        _, tx, ty = best2[1], best2[2]

    # Choose move that minimizes Chebyshev distance to target; avoid obstacles and prefer also increasing opponent distance when denying
    bestm = (10**9, 10**9, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_valid(nx, ny): 
            continue
        dnt = max(abs(tx - nx), abs(ty - ny))
        dno = max(abs(ox - nx), abs(oy - ny))
        # tie-breaker: prioritize moves that move away from opponent when we are behind on target
        rx, ry = (tx, ty)
        ds_now = max(abs(rx - sx), abs(ry - sy))
        do_now = max(abs(rx - ox), abs(ry - oy))
        away_bias = -dno if do_now <= ds_now else dno
        cand = (dnt, away_bias, (dx, dy))
        if cand < bestm:
            bestm = cand

    if bestm[2] is None:
        return [0, 0]
    return [bestm[2][0], bestm[2][1]]