def choose_move(observation):
    W = observation["grid_width"]; H = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obs:
                res.append(t)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def legal(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Immediate pickup if possible
    rset = set(res)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny) and (nx, ny) in rset:
            return [dx, dy]

    # Potential: choose move maximizing (opp_dist - my_dist) to best reachable resource,
    # with a small tie-break to prefer advancing toward resources.
    best_val = -10**18
    best_move = (0, 0)

    # Deterministic tie-break order: already in moves order; ensure strict '>' only.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        if res:
            my_best_gap = -10**18
            my_advance = 10**9
            for (rx, ry) in res:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer resources where opponent is farther from completion than we are.
                gap = d_op - d_me
                if d_me < my_advance:
                    my_advance = d_me
                if gap > my_best_gap:
                    my_best_gap = gap
            # Encourage getting closer to some resource too, without overriding gap.
            val = my_best_gap * 1000 - my_advance
        else:
            # No resources: move toward center while avoiding obstacles.
            cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
            dist = abs(nx - cx) + abs(ny - cy)
            val = -dist

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]