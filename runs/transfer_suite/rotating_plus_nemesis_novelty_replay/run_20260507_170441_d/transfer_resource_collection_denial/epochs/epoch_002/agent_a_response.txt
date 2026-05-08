def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}
    cand = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if not resources:
        # If no visible resources, drift toward the farthest-from-opponent corner to reduce immediate contest
        tx = 0 if ox > w - 1 - ox else w - 1
        ty = 0 if oy > h - 1 - oy else h - 1
        best = [0, 0]
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: 
                continue
            v = -d2(nx, ny, tx, ty) - d2(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Target is the resource that is most advantageous after this move.
        # Advantage: we want (opp_dist - our_dist) large, and also overall closeness.
        best_resource_val = -10**18
        for rx, ry in resources:
            ourd = d2(nx, ny, rx, ry)
            oppd = d2(ox, oy, rx, ry)
            # If we are much closer than opponent, prioritize; otherwise lightly prefer proximity.
            val = (oppd - ourd) * 1000 - ourd + (d2(nx, ny, ox, oy) * 0.01)
            if val > best_resource_val:
                best_resource_val = val

        # Small extra bias: move that also decreases our distance to the overall best resource helps stability.
        # (Compute quickly by reusing best_resource_val structure; use direct nearest-to-we-win resource approximation.)
        nearest_ours = min(d2(nx, ny, rx, ry) for rx, ry in resources)
        total = best_resource_val - nearest_ours * 0.001
        if total > best_val:
            best_val, best_move = total, [dx, dy]

    return best_move