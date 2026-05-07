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
            obstacles.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None
    ox = int(ox) if opp_exists else None
    oy = int(oy) if opp_exists else None

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    respos = []
    for r in resources:
        try:
            x, y = r
            respos.append((int(x), int(y)))
        except:
            pass

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if not respos:
            val = 0
        else:
            # Margin score: prefer resources where we are closer than opponent (deny).
            best_margin = -10**9
            best_my = 10**9
            for rx, ry in respos:
                myd = abs(nx - rx) + abs(ny - ry)
                if myd < best_my:
                    best_my = myd
                if opp_exists:
                    oppd = abs(ox - rx) + abs(oy - ry)
                    margin = oppd - myd
                else:
                    margin = 0
                if margin > best_margin:
                    best_margin = margin

            # Also keep greedy progress toward some resource.
            val = (2.5 * best_margin) - (1.0 * best_my)

            # Tiny tie-break toward staying in bounds toward nearest resource direction.
            # Deterministic based on dx,dy ordering already; add nothing.

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]