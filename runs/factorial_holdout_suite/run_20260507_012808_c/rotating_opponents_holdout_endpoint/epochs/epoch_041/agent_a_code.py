def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        our_min = 10**9
        opp_min = 10**9
        best_diff = -10**9
        best_our = 10**9

        for rx, ry in resources:
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_our < our_min: our_min = d_our
            if d_opp < opp_min: opp_min = d_opp
            diff = d_opp - d_our
            if diff > best_diff or (diff == best_diff and d_our < best_our):
                best_diff = diff
                best_our = d_our

        # Prefer positions where we are closer than opponent to a resource.
        score_key = (best_diff, -best_our, -our_min, opp_min)
        if best_key is None or score_key > best_key:
            best_key = score_key
            best = [dx, dy]

    return [int(best[0]), int(best[1])]