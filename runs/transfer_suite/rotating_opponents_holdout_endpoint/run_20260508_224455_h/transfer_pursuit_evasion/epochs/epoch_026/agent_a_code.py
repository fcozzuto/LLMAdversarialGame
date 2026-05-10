def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_pursuer = ("pursuer" in role) or ("pursue" in role) or ("chaser" in role) or ("pursuit" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    neighbors_block = {}
    for x in range(w):
        for y in range(h):
            cnt = 0
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                if (x+dx, y+dy) in obs:
                    cnt += 1
            neighbors_block[(x,y)] = cnt

    best = [0, 0]
    best_score = -10**18 if i_pursuer else 10**18

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if not i_pursuer:
        # prefer farthest corner from pursuer, then farthest distance
        far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
        tx, ty = far_corner
    else:
        # if pursuer, prefer direct interception; also bias toward reducing evader mobility
        tx, ty = ox, oy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_target = manh(nx, ny, tx, ty)
        d_to_opp = manh(nx, ny, ox, oy)
        if i_pursuer:
            # capture when same cell (d_to_opp == 0): heavily favored
            score = -1000 * d_to_opp - 2 * neighbors_block.get((nx, ny), 0) + 0.5 * (8 - d_to_target)
            # also slightly punish moving away
            score -= 0.1 * (d_to_target - manh(sx, sy, tx, ty))
            if score > best_score:
                best_score = score
                best = [dx, dy]
        else:
            # evader: maximize distance and corner distance; avoid getting surrounded
            score = 1000 * d_to_opp + 2 * neighbors_block.get((nx, ny), 0) + 0.5 * d_to_target
            # prefer not stepping into tight regions (more adjacent obstacles -> worse)
            score -= 3 * (neighbors_block.get((nx, ny), 0))
            if score < best_score:
                best_score = score
                best = [dx, dy]

    return [int(best[0]), int(best[1])]