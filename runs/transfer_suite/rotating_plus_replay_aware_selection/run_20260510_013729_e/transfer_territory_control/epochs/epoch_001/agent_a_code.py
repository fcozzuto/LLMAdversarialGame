def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((a, b) for a, b in observation.get("obstacles", []))
    self_ter = set((a, b) for a, b in observation.get("self_territory", []))
    opp_ter = set((a, b) for a, b in observation.get("opponent_territory", []))
    unclaimed = set((a, b) for a, b in observation.get("unclaimed_cells", []))
    attractive = opp_ter | unclaimed
    if not attractive:
        attractive = unclaimed if unclaimed else self_ter
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(a, b): return abs(a[0]-b[0]) if False else max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    best = None
    # Prefer reaching opponent territory; then unclaimed; then keeping distance from opponent a bit.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue
        dest = (nx, ny)
        if dest in self_ter:
            base = 0
        elif dest in opp_ter:
            base = 4
        elif dest in unclaimed:
            base = 2
        else:
            base = 1
        # Distance to nearest attractive cell (to keep pushing frontiers deterministically).
        if attractive:
            md = None
            for t in attractive:
                d = max(abs(nx - t[0]), abs(ny - t[1]))
                if md is None or d < md:
                    md = d
            md = md if md is not None else 0
        else:
            md = max(abs(nx-ox), abs(ny-oy))
        # Slight preference to not walk directly into opponent where possible.
        od = max(abs(nx - ox), abs(ny - oy))
        score = (base, -md, od)
        if best is None or score > best[0]:
            best = (score, (dx, dy))
    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]