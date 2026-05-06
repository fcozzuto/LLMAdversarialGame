def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in ob
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_key = None
    best_move = [0, 0]

    # Heuristic: prioritize resources I can reach before opponent; then maximize advantage;
    # slight penalty if opponent also gets a fast access.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        my_best = -10**9
        opp_best = 10**9
        take_now = 0
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry) and (rx, ry) != (nx, ny):
                continue
            d_me = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            if d_me == 0:
                take_now = 1
            # Advantage: if I arrive first, big positive; if tie/behind, smaller or negative.
            if d_me < d_opp:
                adv = (d_opp - d_me) + 3  # contested preference
            else:
                adv = -(d_me - d_opp)  # avoid walking into opponent advantage
            if adv > my_best:
                my_best = adv
            if d_opp < opp_best:
                opp_best = d_opp

        # Reduce opponent ability: prefer moving so that opponent's nearest resource distance increases.
        # Also bias slightly toward center to avoid deadlocks.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_pen = -(abs(nx - cx) + abs(ny - cy))

        # Key: maximize take_now, then my_best, then center_pen; minimize opp_best.
        key = (-(take_now), -(my_best), opp_best, -(center_pen), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]