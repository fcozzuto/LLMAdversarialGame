def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(nx, ny):
        return (nx if 0 <= nx < w else x, ny if 0 <= ny < h else y)
    def cd(a, b, c, d):
        da = abs(a-c); db = abs(b-d)
        return da if da > db else db
    if not resources:
        options = []
        for dx, dy in moves:
            nx, ny = clamp(x+dx, y+dy)
            if (nx, ny) in obs:
                continue
            options.append((dx, dy))
        return options[0] if options else [0, 0]
    best = None
    for dx, dy in moves:
        nx, ny = clamp(x+dx, y+dy)
        if (nx, ny) in obs:
            continue
        best_adv = None
        best_self = None
        for rx, ry in resources:
            self_d = cd(nx, ny, rx, ry)
            opp_d = cd(ox, oy, rx, ry)
            adv = opp_d - self_d
            if best_adv is None or adv > best_adv or (adv == best_adv and self_d < best_self):
                best_adv = adv
                best_self = self_d
        score = (best_adv * 1000) - best_self
        cand = (score, dx, dy)
        if best is None or cand > best:
            best = cand
    if best is None:
        for dx, dy in moves:
            nx, ny = clamp(x+dx, y+dy)
            if (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]