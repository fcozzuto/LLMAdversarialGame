def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue

        # Greedy opponent response per resource (1-step toward that resource).
        val = 0
        for rx, ry in resources:
            # our distance after move
            dm = cheb(nx, ny, rx, ry)

            # opponent next step if it targets this resource
            best_do = 10**9
            for odx, ody in moves:
                tx, ty = ox + odx, oy + ody
                if not legal(tx, ty):
                    continue
                do = cheb(tx, ty, rx, ry)
                if do < best_do:
                    best_do = do

            adv = best_do - dm  # positive means we're closer than opponent next step
            if adv > 0:
                # prioritize securing nearer resources with a spread favoring bigger advantage
                val += (adv * 6) + (20 - dm)
            else:
                # still slightly prefer moves that don't let opponent gain too much
                val += adv * 2

        # add small term to keep pressure toward some resource overall
        nearest_dm = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        val -= nearest_dm

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]