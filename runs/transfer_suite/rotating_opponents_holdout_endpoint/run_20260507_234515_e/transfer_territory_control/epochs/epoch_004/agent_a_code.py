def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))
    unclaimed = observation.get("unclaimed_cells", []) or []
    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p[0], p[1]
            un.append((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    self_terr = observation.get("self_territory", []) or []
    st = set()
    for p in self_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            st.add((p[0], p[1]))

    opp_terr = observation.get("opponent_territory", []) or []
    ot = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ot.add((p[0], p[1]))

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best = None
    bestv = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d_un = 10**9
        for x, y in un:
            d = dist(nx, ny, x, y)
            if d < d_un:
                d_un = d
        d_opp = dist(nx, ny, ox, oy)
        adj_st = 0
        adj_ot = 0
        for ddx, ddy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in st:
                adj_st += 1
            if (ax, ay) in ot:
                adj_ot += 1
        v = (-d_un if un else 0) + 0.8 * adj_st + 0.2 * d_opp - 0.6 * adj_ot
        if v > bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best