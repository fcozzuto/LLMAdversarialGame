def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def occ(x, y):
        return (x, y) in obst

    def near_obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obst:
                    p += 1
        return p

    if not resources:
        return [0, 0]

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if occ(nx, ny):
            continue

        # New policy: prefer moves that create an immediate "grip" on the same target
        # the opponent is contesting, while reducing our exposure to obstacles.
        grip = 0
        for rx, ry in resources:
            if occ(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # If opponent is closer, try to narrow the gap aggressively.
            gap = do - ds
            # Strongly favor being close even if not ahead yet (enables capture race).
            closeness = 8 - ds
            if closeness < 0:
                closeness = 0

            # If we can already reach as fast or faster, big bonus (contested capture).
            ahead = 1 if gap >= 0 else 0
            val = gap * 5 + closeness * (2 if ahead else 1)

            # Also discourage chasing resources that are far from us while opponent is already very close.
            if gap < 0 and do <= 2 and ds > 3:
                val -= 20

            if val > grip:
                grip = val

        # Secondary: reduce opponent access by moving toward contested "frontiers"
        # (move that also lowers our distance to opponent can help deny captures).
        opp_dist = cheb(nx, ny, ox, oy)
        opp_bonus = 10 - opp_dist
        if opp_bonus < 0:
            opp_bonus = 0

        v = grip + opp_bonus - 2 * near_obst_pen(nx, ny)

        if v > bestv:
            bestv = v
            best = [dx, dy]

    # If somehow no valid move, stay.
    return best