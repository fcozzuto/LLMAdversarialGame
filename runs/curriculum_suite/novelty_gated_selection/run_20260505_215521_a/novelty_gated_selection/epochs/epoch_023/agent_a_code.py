def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w - 1, h - 1
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            key = (man(nx, ny, tx, ty), (dx, dy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Novel policy: "advantage targeting" + short-horizon anti-sweep (deny opponent)
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        # Advantage against opponent: prefer states where we are strictly closer to some resource
        best_res = None
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Encourage resources where self is closer; penalize those where opponent is much closer
            advantage = d_opp - d_self
            # Tie-break: closer self
            cand = (-(advantage), d_self, man(nx, ny, rx, ry))
            if best_res is None or cand < best_res:
                best_res = cand

        # Anti-sweep: if opponent is likely moving along rows, keep distance to their current row targets
        opp_row = oy
        row_pen = abs(ny - opp_row)
        opp_pos_pen = man(nx, ny, ox, oy)

        # Lower is better
        score = (best_res[0], best_res[1], row_pen, opp_pos_pen, (dx, dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move