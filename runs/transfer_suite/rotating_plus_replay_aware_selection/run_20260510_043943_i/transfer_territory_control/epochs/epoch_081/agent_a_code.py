def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                targets.append((x, y))
    if not targets:
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if valid(x, y):
                    targets.append((x, y))

    opp_weight = 6
    best = None
    best_sc = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer moving closer to the nearest target, and away from opponent.
            sc = 0
            if targets:
                md = 10**9
                for tx, ty in targets:
                    d = abs(nx - tx) + abs(ny - ty)
                    if d < md:
                        md = d
                sc += 1000 - 20 * md
            dO = abs(nx - ox) + abs(ny - oy)
            sc += opp_weight * dO
            if best is None or sc > best_sc:
                best_sc = sc
                best = (dx, dy)

    if best is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]