def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors_free(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    def obs_prox(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p -= 3
        return p

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def score_move(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        if is_evader:
            d_score = d
        else:
            d_score = -d

        hit_obs = -10**6 if (nx, ny) in obs else 0
        nf = neighbors_free(nx, ny) * (1.0 if is_evader else 0.5)
        prox = obs_prox(nx, ny)
        ed = edge_dist(nx, ny)
        # Evader: avoid getting too close to walls; Pursuer: prefer reducing edge distance only mildly.
        edge_score = (ed * (-0.4) if is_evader else ed * (0.15))
        return hit_obs + d_score * (3.0 if is_evader else 2.0) + nf + prox + edge_score

    best_move = [0, 0]
    best_val = None
    # Deterministic tie-break: fixed ordering of deltas.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_move(nx, ny)
        if best_val is None or v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move