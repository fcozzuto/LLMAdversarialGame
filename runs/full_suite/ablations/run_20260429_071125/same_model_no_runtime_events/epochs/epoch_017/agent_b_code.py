def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and r["pos"] is not None and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            elif "x" in r and "y" in r and r["x"] is not None and r["y"] is not None:
                resources.append((int(r["x"]), int(r["y"])))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources or not valid(sx, sy):
        return [0, 0]

    opp_min = min(cheb(ox, oy, rx, ry) for rx, ry in resources)

    best = None
    best_adv = -10**9
    best_resd = 10**9
    best_oppd = 10**9

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_min = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            # advantage: how much closer we are than opponent's current closest resource
            adv = opp_min - my_min
            opp_to_mypos = cheb(ox, oy, nx, ny)
            my_to_opp = opp_to_mypos
            # deterministic tie-breaks: maximize adv, then minimize my_min, then minimize distance from opponent (can help contest), then prefer movement
            if (adv > best_adv or
                (adv == best_adv and my_min < best_resd) or
                (adv == best_adv and my_min == best_resd and my_to_opp < best_oppd) or
                (adv == best_adv and my_min == best_resd and my_to_opp == best_oppd and (abs(dx) + abs(dy) < (abs(best[0]) + abs(best[1])) if best is not None else True))):
                best_adv = adv
                best_resd = my_min
                best_oppd = my_to_opp
                best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]