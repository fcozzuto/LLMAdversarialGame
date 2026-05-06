def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = 0 if sx > w - 1 - sx else w - 1
        ty = 0 if sy > h - 1 - sy else h - 1
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy): return [dx, dy]
        for mdx, mdy in moves:
            if valid(sx + mdx, sy + mdy): return [mdx, mdy]
        return [0, 0]

    def man(a, b, x, y): return abs(x - a) + abs(y - b)
    # Edge-patrol bias: resources near edges (common opponent corridor) but we want ones we can beat.
    def edge_score(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    def best_target():
        best = None
        bx, by = 0, 0
        for (rx, ry) in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Opponent likely to stay near edges close to its side: prefer those edges (low edge_score).
            es = edge_score(rx, ry)
            # We want od - sd large (can arrive first), and es small (edge corridor).
            score = (od - sd) * 100 - es
            if best is None or score > best or (score == best and (sd < man(sx, sy, bx, by))):
                best = score
                bx, by = rx, ry
        return bx, by

    tx, ty = best_target()

    def escape_bonus(x, y):
        # Avoid stepping into tight spots.
        c = 0
        for mdx, mdy in moves:
            nx, ny = x + mdx, y + mdy
            if valid(nx, ny): c += 1
        return c

    best_move = [0, 0]
    best_val = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny): 
            continue
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Evaluate: faster to target than opponent would be at that moment; also keep some distance from opponent.
        oppd_next = man(nx, ny, ox, oy)
        val = (od - sd) * 120 + (oppd_next) * 2 + escape_bonus(nx, ny)
        # If tied, prefer moves that actually reduce distance to target.
        cur_sd = man(sx, sy, tx, ty)
        if val > best_val or (val == best_val and sd < cur_sd):
            best_val = val
            best_move = [mdx, mdy]

    return best_move