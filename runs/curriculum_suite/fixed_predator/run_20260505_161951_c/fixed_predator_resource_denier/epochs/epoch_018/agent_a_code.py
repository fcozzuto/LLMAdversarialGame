def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # keep far from opponent; also gently drift to opposite corner from opponent
            tx = w - 1 if ox == 0 else 0
            ty = h - 1 if oy == 0 else 0
            v = d * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    # opportunistic_switcher: decide per turn whether to chase a resource that is currently "safer" than opponent,
    # otherwise maximize distance gain on the best available resource.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        move_v = -10**18
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # favor cells that make us at least as competitive as opponent, and that progress toward capture
            rel = opp_d - self_d
            # if we move onto a resource (capture adjacency), strongly prefer
            capture_bonus = 2000 if (nx == rx and ny == ry) else 0
            # discourage stepping into a local trap near obstacles by penalizing adjacency to obstacles
            trap = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    px, py = nx + ax, ny + ay
                    if 0 <= px < w and 0 <= py < h and (px, py) in obstacle_set:
                        trap += 1
            v = rel * 120 - self_d * 6 + capture_bonus - trap * 2
            # small tie-break: prefer moving toward center to keep options open
            v -= abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
            if v > move_v:
                move_v = v
        if move_v > bestv or (move_v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = move_v
            best = [dx, dy]
    return best