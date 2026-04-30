def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cd(a, b, c, d): 
        dx = abs(a-c); dy = abs(b-d)
        return dx if dx > dy else dy
    opp_dists = {res: cd(ox, oy, res[0], res[1]) for res in resources}
    best_res = None
    best_score = 10**9
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = opp_dists[(rx, ry)]
        score = ds - 0.6 * do + (0.15 * (ds + do))
        if score < best_score:
            best_score = score
            best_res = (rx, ry)
    if not best_res:
        best = (0, 0); bd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            d = cd(nx, ny, ox, oy)
            if d > bd: bd = d; best = (dx, dy)
        return [best[0], best[1]]
    rx, ry = best_res
    best = (0, 0); best_h = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: 
            continue
        ds = cd(nx, ny, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer reaching resource sooner; if tied, increase distance to opponent.
        h = ds - 0.7 * do + 0.05 * (ds + do) - 0.02 * cd(nx, ny, ox, oy)
        # Small bias to keep moving generally toward target.
        h += 0.001 * (abs(nx - rx) + abs(ny - ry))
        if h < best_h:
            best_h = h
            best = (dx, dy)
    return [best[0], best[1]]