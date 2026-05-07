def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    res_list = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [-1, 0, 1]
    respos = []
    for r in res_list:
        try:
            respos.append((r[0], r[1]))
        except:
            pass

    def best_resource():
        if not respos:
            return None
        best = None
        best_key = None
        for rx, ry in respos:
            myd = abs(sx - rx) + abs(sy - ry)
            oppd = 10**9
            if ox is not None and oy is not None:
                oppd = abs(ox - rx) + abs(oy - ry)
            # Prefer resources we can reach not much later than opponent; break ties by closeness.
            key = (max(myd - oppd, 0), myd)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource()

    if target is None:
        # If no resources visible, drift toward center while avoiding obstacles.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    candidates = []
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp = (ox, oy) if ox is not None and oy is not None else None

    best_move = None
    best_score = None
    for dx, dy, nx, ny in candidates:
        myd = abs(nx - tx) + abs(ny - ty)
        score = -myd
        if opp is not None:
            # Push away from opponent while still approaching the target.
            score += 0.25 * (abs(nx - ox) + abs(ny - oy))
            # If targeting a resource, also prefer moves that don't let opponent close the gap too much.
            if target is not None:
                my_now = abs(sx - tx) + abs(sy - ty)
                opp_now = abs(ox - tx) + abs(oy - ty)
                my_next = myd
                opp_next = abs(ox - tx) + abs(oy - ty)
                # (opp_next constant here since opponent doesn't move); keep it simple and robust.
                score += 0.1 * (my_now - my_next)
                score += 0.05 * (opp_now - opp_now)
        # Mild tie-break: prefer diagonal/forward progress.
        score += 0.01 * (abs(dx) + abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]