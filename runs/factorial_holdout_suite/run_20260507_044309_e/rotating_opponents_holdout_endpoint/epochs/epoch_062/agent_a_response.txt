def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Decide target by "arrive first" margin; if tied, prefer best advantage; then closest.
    best = None
    for rx, ry in resources:
        ds = king((sx, sy), (rx, ry))
        do = king((ox, oy), (rx, ry))
        margin = do - ds  # positive means we arrive earlier or equal advantage
        score = (margin, -ds, -abs(rx - (w - 1 - sx)) - abs(ry - (h - 1 - sy)))
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    _, (tx, ty) = best

    # Choose next step greedily, avoiding obstacles; tie-break by fixed order to stay deterministic.
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = king((nx, ny), (tx, ty))
        # Also slightly reduce opponent ability by moving away from opponent-target line (simple proxy).
        od = king((nx, ny), (ox, oy))
        cand.append((nd, od, dx, dy))
    cand.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
    if not cand:
        return [0, 0]
    return [int(cand[0][2]), int(cand[0][3])]