def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
                nx, ny = sx, sy
            v = -((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)) - (abs(ox - nx) + abs(oy - ny)) * 0.01
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best
    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy
    # Consider a small deterministic subset: closest to us
    scored = []
    for r in resources:
        rx, ry = r[0], r[1]
        scored.append((d2(sx, sy, rx, ry), rx, ry))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    top = scored[:6] if len(scored) > 6 else scored
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obs_set:
            nx, ny = sx, sy
        my_to_opp = d2(nx, ny, ox, oy)
        # Evaluate advantage toward contested resources
        val = 0.0
        for _, rx, ry in top:
            myd = d2(nx, ny, rx, ry)
            oppd = d2(ox, oy, rx, ry)
            # Prefer moving to resources where we get/keep a lead
            val += (oppd - myd) * 1.0
            # Mild preference for reducing own distance
            val += -0.01 * myd
        # Small safety term: avoid giving opponent an easy immediate approach
        val += -0.001 * my_to_opp
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move