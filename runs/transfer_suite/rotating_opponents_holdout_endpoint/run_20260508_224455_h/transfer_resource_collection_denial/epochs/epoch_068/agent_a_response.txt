def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    row_pref = -1 if oy < sy else (1 if oy > sy else 0)

    best = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # We want to reach earlier than opponent; also bias toward "behind" relative rows
        target_score = (od - sd) * 10 - sd + row_pref * (ry - sy)
        if best is None or target_score > best[0]:
            best = (target_score, rx, ry)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    # Prefer diagonal/axis steps that reduce cheb distance; deterministic tie-break by order
    deltas = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy), (0, 0)]
    seen = set()
    for mx, my in deltas:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # small penalty if moving closer to opponent to avoid denier swipes
        opp_dist = cheb(nx, ny, ox, oy)
        candidates.append((dist, -opp_dist, mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]