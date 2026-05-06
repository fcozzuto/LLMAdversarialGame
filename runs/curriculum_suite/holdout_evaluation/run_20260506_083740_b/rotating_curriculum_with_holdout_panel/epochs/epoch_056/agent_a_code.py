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
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def valid(x, y): return inb(x, y) and (x, y) not in ob

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_score = -10**18

    # If we're already on a resource, try to stay (deterministic); otherwise pick best next.
    if any(r and len(r) >= 2 and int(r[0]) == sx and int(r[1]) == sy for r in resources):
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if valid(ox, oy) is False:
            opp_dist_pen = 0
        else:
            opp_dist_pen = -md(nx, ny, ox, oy)  # generally keep distance from opponent

        # Choose the resource that gives best advantage from the next cell
        best_adv = -10**18
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            my_d = md(nx, ny, rx, ry)
            op_d = md(ox, oy, rx, ry)
            if my_d == 0:
                adv = 10**9
            else:
                # We want op to be farther than us; also prefer nearer targets.
                adv = (op_d - my_d) * 200 - my_d * 5
                # If opponent is extremely close, de-prioritize (they may snatch first).
                if op_d <= 2:
                    adv -= 600
                elif op_d <= 3:
                    adv -= 200
            if adv > best_adv:
                best_adv = adv

        # Encourage moving toward center only if no strong resource advantage exists
        if best_adv < -10**17:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        else:
            center_bias = -md(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0) * 0.01

        score = best_adv + opp_dist_pen + center_bias
        # Tie-break deterministically: prefer smaller dx then smaller dy, then staying still.
        key = (score, -1 if dx == 0 and dy == 0 else 0, -abs(dx), -abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best is not None else [0, 0]