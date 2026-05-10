def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    opp_next = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if legal(nx, ny):
            opp_next.append((nx, ny))
    if not opp_next:
        opp_next = [(ox, oy)]

    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_key = None
    for mydx, mydy in moves:
        mx, my = sx + mydx, sy + mydy
        if not legal(mx, my):
            continue
        worst = None
        for px, py in opp_next:
            if mx == px and my == py:
                score = 1000000
            else:
                score = -d2(mx, my, px, py)
            if worst is None or score > worst:
                worst = score  # opponent maximizes this score
        # our objective: maximize opponent's best (i.e., minimize distance / enable capture)
        # Key: primarily maximize worst score; then prefer lower distance to current opponent.
        key = (worst, -abs(mx - ox) - abs(my - oy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (mydx, mydy)

    return [int(best_move[0]), int(best_move[1])]