def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    respos = []
    for r in resources:
        try:
            x, y = r
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                respos.append((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not respos:
        # No resources visible: move toward opponent if possible, else towards center-ish (deterministic)
        tx = w // 2
        ty = h // 2
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -abs(nx - tx) - abs(ny - ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        for rx, ry in respos:
            d_self = abs(nx - rx) + abs(ny - ry)
            if opp_exists:
                d_opp = abs(ox - rx) + abs(oy - ry)
            else:
                d_opp = d_self + 10
            # Prefer resources we can reach sooner than opponent; also prefer being closer overall.
            v = max(v, (-d_self) + 0.35 * d_opp + (-0.05 * d_self * (1 if d_self == 0 else 1)))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]