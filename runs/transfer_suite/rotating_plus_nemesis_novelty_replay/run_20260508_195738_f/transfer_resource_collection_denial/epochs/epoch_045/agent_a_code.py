def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def manh(a, b, c, d): return abs(a - c) + abs(b - d)
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        best = None; bestv = None
        for cx, cy in corners:
            if not inb(cx, cy): 
                continue
            v = (manh(ox, oy, cx, cy), -manh(sx, sy, cx, cy))
            if bestv is None or v > bestv:
                bestv = v; best = (cx, cy)
        tx, ty = (best if best is not None else (sx, sy))
        bestm = [0, 0]; bestmv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = (manh(ox, oy, nx, ny), -manh(sx, sy, nx, ny))
            if bestmv is None or v > bestmv:
                bestmv = v; bestm = [dx, dy]
        return bestm

    bestres = None; bestscore = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        if bestscore is None:
            bestscore = (0, 0)
        # Prefer arriving no later; then smaller self distance; then tie by farther from opponent
        cand = (sd <= od, -sd, od - sd, -rx, -ry)
        if bestres is None or cand > bestscore:
            bestscore = cand; bestres = (rx, ry)

    tx, ty = bestres
    # Choose move that improves our lead towards target and reduces opponent's lead
    bestm = [0, 0]; bestmv = None
    cur_sd = manh(sx, sy, tx, ty); cur_od = manh(ox, oy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = manh(nx, ny, tx, ty)
        nod = manh(ox, oy, tx, ty)  # opponent position unchanged this step
        # Primary: minimize our distance and aim to be <= opponent; Secondary: make lead bigger
        v = (nsd <= nod, -(nsd - cur_sd), (cur_od - nsd), -nsd, -abs((tx - nx)) - abs((ty - ny)))
        if bestmv is None or v > bestmv:
            bestmv = v; bestm = [dx, dy]
    return bestm