def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a resource we can beat, otherwise deny their best by going for something they are far from
    ahead = []
    behind = []
    for rx, ry in resources:
        selfd = md(x, y, rx, ry)
        oppd = md(ox, oy, rx, ry)
        if selfd <= oppd:
            ahead.append((selfd, rx, ry, oppd))
        else:
            behind.append((oppd, selfd, rx, ry))
    if ahead:
        ahead.sort(key=lambda t: (t[0], t[1], t[2]))
        _, tx, ty, _ = ahead[0]
    else:
        behind.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
        _, _, tx, ty = behind[0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_move = [0, 0]
    self_cur = md(x, y, tx, ty)
    opp_cur = md(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        # Prefer moves that increase our lead (tie-break by closer self distance then stable dx,dy)
        lead_after = no - ns
        lead_cur = opp_cur - self_cur
        gain = lead_after - lead_cur
        val = (gain, lead_after, -ns, dx, dy)
        if best is None or val > best:
            best = val
            best_move = [dx, dy]

    return best_move