def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        ddx = a - c
        if ddx < 0: ddx = -ddx
        ddy = b - d
        if ddy < 0: ddy = -ddy
        return ddx + ddy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best_score = -10**18
    best_move = [0, 0]

    opp_dist_weight = 1.25
    own_dist_weight = 1.0
    block_bonus = 0.15
    obst_repulse = 0.18

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_min = 10**9
        opp_min = 10**9
        my_second = 10**9
        for rx, ry in resources:
            d1 = man(rx, ry, nx, ny)
            if d1 < my_min:
                my_second = my_min
                my_min = d1
            elif d1 < my_second:
                my_second = d1
            d2 = man(rx, ry, ox, oy)
            if d2 < opp_min:
                opp_min = d2

        # if we can beat opponent on a reachable resource, value it; otherwise head toward overlap (deny)
        score = -own_dist_weight * my_min + opp_dist_weight * opp_min
        if my_second < 10**9:
            score += block_bonus / (1 + my_second)

        # obstacle repulsion (discourage moves adjacent to obstacles)
        neigh_rep = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx2 = nx + ax
                ty2 = ny + ay
                if (tx2, ty2) in obstacles:
                    neigh_rep += 1
        score -= obst_repulse * neigh_rep

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move