def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best_r = None
    best_adv = -10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and (rx, ry) < best_r):
            best_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r
    if best_adv >= 0:
        goalx, goaly = rx, ry
    else:
        stepx = 0 if rx == ox else (1 if rx > ox else -1)
        stepy = 0 if ry == oy else (1 if ry > oy else -1)
        goalx, goaly = ox + stepx, oy + stepy
        if not inb(goaly if False else goalx, goaly):  # harmless deterministic guard
            goalx, goaly = rx, ry
        if (goalx, goaly) in obstacles:
            goalx, goaly = rx, ry

    # Prefer reducing distance to goal; add small tie-break to stay away from opponent when contesting.
    best = None
    for dx, dy, nx, ny in legal:
        dgoal = cheb(nx, ny, goalx, goaly)
        dop = cheb(nx, ny, ox, oy)
        # When goal is the blocking cell (opponent is closer), prioritize not giving immediate advantage.
        contest = 1 if (best_adv < 0 and (goalx, goaly) == (ox + (0 if rx == ox else (1 if rx > ox else -1)), oy + (0 if ry == oy else (1 if ry > oy else -1)))) else 0
        val = (dgoal, dop if contest else 0, dx