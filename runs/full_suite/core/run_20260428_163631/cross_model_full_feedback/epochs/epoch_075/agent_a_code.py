def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource that we can pressure (largest distance advantage)
    if resources:
        candidates = []
        for rx, ry in resources:
            dr_our = abs(rx - sx) + abs(ry - sy)
            dr_opp = abs(rx - ox) + abs(ry - oy)
            # Primary: opp advantage over us (bigger is better for us -> negative of our advantage)
            press = dr_opp - dr_our
            candidates.append((press, -dr_our, rx, ry))
        candidates.sort(reverse=True)
        tr = candidates[0][2], candidates[0][3]
        tx, ty = tr

        best = None
        for dx, dy, nx, ny in legal:
            our_to = abs(tx - nx) + abs(ty - ny)
            opp_to = abs(tx - ox) + abs(ty - oy)
            # After move, prefer being closer to target and not allowing opponent to be closer next
            # (opponent position static => use current comparison as proxy)
            current_adv = opp_to - our_to
            # Also avoid stepping into a square that increases our min distance to any resource too much
            min_res_now = 10**9
            for rx, ry in resources:
                d = abs(rx - nx) + abs(ry - ny)
                if d < min_res_now:
                    min_res_now = d
            score = (current_adv, -our_to, -min_res_now, -abs(nx - ox) - abs(ny - oy), -nx, -ny)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    # No resources: move to center while maximizing distance from opponent, deterministic tie-break
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy, nx, ny in legal:
        dcen = abs(nx - cx) + abs(ny - cy)
        dopp = abs(nx - ox) + abs(ny - oy)
        score = (dopp, -dcen, -nx, -ny)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]