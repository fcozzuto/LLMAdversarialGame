def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def frontier_gain(nx, ny):
        if (nx, ny) in obs:
            return -10**6
        g = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if not inb(ax, ay):
                    continue
                if (ax, ay) in unclaimed:
                    g += 1
                elif (ax, ay) in opp:
                    g += 0.25
        return g

    # Deterministic tiebreak: fixed ordering and lexicographic fallback
    cand = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        # Primary: capture nearby / expand toward center
        distc = abs(nx - cx) + abs(ny - cy)
        gain = frontier_gain(nx, ny)

        # Secondary: prefer moving into opponent territory only if it improves closeness to center
        inopp = (nx, ny) in opp
        inuncl = (nx, ny) in unclaimed
        instay = (dx == 0 and dy == 0)

        opp_dist = 10**9
        if opp:
            # small deterministic approx: min over up to 8 opponent cells (sorted)
            olist = sorted(opp)[:8]
            for px, py in olist:
                d = abs(px - nx) + abs(py - ny)
                if d < opp_dist:
                    opp_dist = d

        # Heuristic value
        v = 0.0
        v += (6.0 - distc) * 2.2
        v += gain * (5.0 if inuncl else 3.0)
        if inopp:
            v += 18.0
            v -= max(0, opp_dist - 1) * 0.8
        else:
            v -= opp_dist * 0.08
        if instay:
            v -= 0.7
        if (nx, ny) in selft:
            v -= 0.6  # encourage leaving current territory to expand

        cand.append((v, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = cand[0]
    return [int(dx), int(dy)]