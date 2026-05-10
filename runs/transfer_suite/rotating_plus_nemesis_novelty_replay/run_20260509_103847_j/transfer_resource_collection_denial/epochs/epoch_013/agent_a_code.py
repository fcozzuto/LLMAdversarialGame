def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def best_target_for_self():
        best = None
        best_key = None
        for r in resources:
            sd = man((sx, sy), r)
            od = man((ox, oy), r)
            # Prefer resources we're relatively closer to; break ties by absolute closeness and then coordinates
            key = (-(od - sd), sd, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best = r
        return best

    target = best_target_for_self()

    def opp_step(pos):
        px, py = pos
        best = (0, 0); best_key = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not inb(nx, ny):
                continue
            d = man((nx, ny), target)
            # minimize opponent distance to target; deterministic tie-break
            key = (d, nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return best

    best_move = (0, 0); best_val = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not inb(nsx, nsy):
            continue
        ods = man((ox, oy), target)
        # simulate opponent choosing step toward same target
        odx, ody = opp_step((ox, oy))
        nosx, nosy = nsx, nsy
        nos_ox, nos_oy = ox + odx, oy + ody

        sd1 = man((nosx, nosy), target)
        od1 = man((nos_ox, nos_oy), target)

        capture_bonus = 3.0 if (nosx, nosy) == target else 0.0
        # maximize relative advantage after one ply; slight preference to reduce both distances
        val = (od1 - sd1) + capture_bonus - 0.01 * (sd1 + od1) - 0.001 * ods
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]