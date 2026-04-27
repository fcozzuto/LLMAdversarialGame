def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def clamp(p):
        x, y = p
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return (x, y)
    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])
    if not resources:
        return [0, 0]
    best = (-10**18, None)
    tx = observation.get("turn_index", 0)
    for dx, dy in dirs:
        nx, ny = clamp((sx+dx, sy+dy))
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            self_d = (nx, ny)
            margin = -10**12
            for r in resources:
                sd = dist(self_d, r)
                od = dist((ox, oy), r)
                v = od - sd
                if v > margin:
                    margin = v
            # slight bias toward reducing our distance to the currently best resource
            # and toward moving generally toward opponent side when margins tie
            tie = margin
            if tie > -10**11:
                # compute minimal self distance to any resource for tie-break
                min_self = min(dist((nx, ny), r) for r in resources)
                adv = margin*100 - min_self
                # deterministic tie-break using turn index
                adv += ((nx*31 + ny*17 + tx) % 7) * 1e-3
                sc = adv
            else:
                sc = margin
        if sc > best[0]:
            best = (sc, (dx, dy))
        elif sc == best[0] and best[1] is not None:
            # deterministic tie: prefer smaller dx, then dy
            if (dx, dy) < best[1]:
                best = (sc, (dx, dy))
    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]