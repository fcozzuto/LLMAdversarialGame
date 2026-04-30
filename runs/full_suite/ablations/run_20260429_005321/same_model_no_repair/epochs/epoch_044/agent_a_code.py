def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)
    res = set((x, y) for x, y in resources)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        p = 0
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            if (x + dx, y + dy) in obs:
                p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not moves:
        return [0, 0]

    best_move = [0, 0]
    best_score = -10**18

    # Ownership: prefer resources where we are at least as close as opponent.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue

        hit = 1 if (nx, ny) in res else 0
        d_to_opp = king_dist(nx, ny, ox, oy)
        pen = obs_pen(nx, ny)

        if resources:
            best_res_score = -10**18
            for rx, ry in resources:
                ds = king_dist(nx, ny, rx, ry)
                do = king_dist(ox, oy, rx, ry)
                # Favor resources where we are closer or parity, and also keep distance small.
                rel = ds - do
                s = (-ds) + (0.9 * (1 if rel <= 0 else -1) * (1 if rel <= 0 else 0.5)) - 0.2 * rel
                if (rx, ry) in res:
                    s += 1.2
                if s > best_res_score:
                    best_res_score = s
            score = 1.5 * hit + (0.95 * best_res_score) + (0.08 * d_to_opp) - 0.15 * pen
        else:
            # No resources: avoid opponent but keep escape routes away from obstacles.
            score = 0.25 * king_dist(nx, ny, ox, oy) - 0.3 * pen

        if score > best_score:
            best_score = score
            best_move = [mx, my]

    return best_move