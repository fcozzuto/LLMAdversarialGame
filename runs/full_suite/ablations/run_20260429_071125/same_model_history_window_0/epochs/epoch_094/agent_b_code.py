def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_adv = None
    best_dself = None

    if resources:
        opp_to_res = [(rx, ry, cheb(rx, ry, ox, oy)) for rx, ry in resources]
        for dxm, dym in deltas:
            nx, ny = sx + dxm, sy + dym
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Evaluate best target from next position
            adv = -10**9
            dself_best = 10**9
            for rx, ry, dopp in opp_to_res:
                dself = cheb(nx, ny, rx, ry)
                a = dopp - dself
                if dself == 0:
                    a += 2
                if a > adv or (a == adv and dself < dself_best):
                    adv = a
                    dself_best = dself
            if best_adv is None or adv > best_adv or (adv == best_adv and dself_best < best_dself):
                best_adv = adv
                best_dself = dself_best
                best = [dxm, dym]
    else:
        # No resources: drift toward center while avoiding obstacles
        for dxm, dym in deltas:
            nx, ny = sx + dxm, sy + dym
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            distc = abs(nx - cx) + abs(ny - cy)
            if best_adv is None or distc < best_adv:
                best_adv = distc
                best = [dxm, dym]

    if best is None:
        return [0, 0]
    return best