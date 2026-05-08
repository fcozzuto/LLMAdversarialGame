def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # if standing on resource, take it
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    # legal moves
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = min(cand, key=lambda t: cheb(t[2], t[3], tx, ty))
        return [best[0], best[1]]

    # pick best resource by advantage, then closeness
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (sd - od, sd)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # choose next step: maximize chance to beat opponent on this target;
    # tie-break toward smaller distance to target, then toward larger chebyshev progress.
    def step_key(dx, dy, nx, ny):
        n_sd = abs(rx - nx) + abs(ry - ny)
        n_od = abs(rx - ox) + abs(ry - oy)  # opponent position unchanged this turn
        adv = (n_sd - n_od)  # smaller is better
        return (adv, n_sd, -cheb(nx, ny, sx, sy))

    best = min(cand, key=lambda t: step_key(t[0], t[1], t[2], t[3]))
    return [best[0], best[1]]