def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("tag" in role)

    deltas = [(-1, -1), (0, -1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Opponent action set: legal moves (stay allowed), avoid obstacles
    opp_moves = []
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            opp_moves.append((dx, dy, nx, ny))
    if not opp_moves:
        opp_moves = [(0, 0, ox, oy)]

    best = None
    best_val = None

    for dx0, dy0 in deltas:
        nsx, nsy = sx + dx0, sy + dy0
        if not inb(nsx, nsy) or (nsx, nsy) in obst:
            # engine will keep us in place; heavily discourage stepping into obstacles/out-of-bounds
            nsx, nsy = sx, sy
            dx0, dy0 = 0, 0

        if is_pursuer:
            # choose our move that minimizes distance in the worst case opponent maximizes it
            worst = -1
            for _, _, nox, noy in opp_moves:
                d = dist2(nsx, nsy, nox, noy)
                if d > worst:
                    worst = d
            val = -worst  # smaller worst distance => larger val
        else:
            # evader: maximize distance under worst-case pursuer minimizing it
            best_op = 10**18
            for _, _, nox, noy in opp_moves:
                d = dist2(nox, noy, nsx, nsy)
                if d < best_op:
                    best_op = d
            val = best_op

        if best is None or val > best_val:
            best = (dx0, dy0)
            best_val = val

    return [int(best[0]), int(best[1])]