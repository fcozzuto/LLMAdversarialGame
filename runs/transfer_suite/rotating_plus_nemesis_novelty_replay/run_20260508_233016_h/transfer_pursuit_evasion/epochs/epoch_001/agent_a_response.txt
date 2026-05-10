def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("evad" not in self_role and "evad" in opp_role)
    dxs = [-1, 0, 1]
    deltas = []
    for dx in dxs:
        for dy in dxs:
            deltas.append([dx, dy])
    if [0, 0] in deltas:
        deltas.remove([0, 0])
        deltas.append([0, 0])
    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)
    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = dist(nx, ny, ox, oy)
        if is_pursuer:
            # Minimize distance to evader (maximize -d). Deterministic tie-break by corner bias.
            corner_bias = (0 if (nx in (0, w-1) and ny in (0, h-1)) else 0.1)
            v = (-d) - corner_bias
        else:
            # Evader: maximize distance from pursuer; also bias toward farthest corner.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(dist(nx, ny, cx, cy) for cx, cy in corners)
            v = d * 2 + far_corner * 0.01
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    if best is None:
        best = [0, 0]
    return [int(best[0]), int(best[1])]